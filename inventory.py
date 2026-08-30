import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class InventoryParams:
	service_level: float = 0.95  # service level for safety stock
	lead_time_days: int = 14     # average supplier lead time in days
	holding_cost_per_unit_per_year: float = 2.0
	ordering_cost_per_order: float = 50.0

# Z-score approximations for common service levels
_SERVICE_Z = {
	0.80: 0.8416,
	0.90: 1.2816,
	0.95: 1.6449,
	0.97: 1.8808,
	0.98: 2.0537,
	0.99: 2.3263,
}

def _z_from_service_level(sl: float) -> float:
	closest = min(_SERVICE_Z.keys(), key=lambda k: abs(k - sl))
	return _SERVICE_Z[closest]

def compute_eoq(annual_demand: float, ordering_cost: float, holding_cost: float) -> float:
	if annual_demand <= 0 or ordering_cost <= 0 or holding_cost <= 0:
		return 0.0
	return np.sqrt((2.0 * annual_demand * ordering_cost) / holding_cost)

def compute_safety_stock(daily_demand_std: float, lead_time_days: float, service_level: float) -> float:
	z = _z_from_service_level(service_level)
	return z * daily_demand_std * np.sqrt(max(lead_time_days, 0.0))

def compute_reorder_point(daily_demand_mean: float, lead_time_days: float, safety_stock: float) -> float:
	return daily_demand_mean * max(lead_time_days, 0.0) + safety_stock

def recommend_inventory(df: pd.DataFrame, params: InventoryParams) -> pd.DataFrame:
	"""
	Expects columns:
	- sku
	- avg_daily_demand
	- std_daily_demand
	- current_stock
	- unit_cost
	- annual_demand (optional; if missing, use avg_daily_demand*365)
	"""
	req_cols = ["sku", "avg_daily_demand", "std_daily_demand", "current_stock", "unit_cost"]
	for c in req_cols:
		if c not in df.columns:
			raise ValueError(f"Missing required column: {c}")

	work = df.copy()
	work["annual_demand"] = work.get("annual_demand", work["avg_daily_demand"] * 365.0)
	work["holding_cost"] = params.holding_cost_per_unit_per_year  # can be unit_cost * rate if preferred

	work["EOQ"] = work.apply(lambda r: compute_eoq(r["annual_demand"], params.ordering_cost_per_order, r["holding_cost"]), axis=1)
	work["SafetyStock"] = work.apply(lambda r: compute_safety_stock(r["std_daily_demand"], params.lead_time_days, params.service_level), axis=1)
	work["ReorderPoint"] = work.apply(lambda r: compute_reorder_point(r["avg_daily_demand"], params.lead_time_days, r["SafetyStock"]), axis=1)

	work["SuggestedOrderQty"] = (work["ReorderPoint"] - work["current_stock"]).clip(lower=0.0)
	work["SuggestedOrderQty"] = np.ceil(work["SuggestedOrderQty"].where(work["SuggestedOrderQty"] > 0, 0))

	return work[["sku", "avg_daily_demand", "std_daily_demand", "current_stock", "EOQ", "SafetyStock", "ReorderPoint", "SuggestedOrderQty"]]


# Optional PuLP import for optimization
_pulp_import_error = None
try:
	import pulp
except Exception as e:  # pragma: no cover
	pulp = None  # type: ignore
	_pulp_import_error = e


def reorder_point_and_safety_stock(daily_mean: float, daily_std: float, lead_time_days: int, service_level: float = 0.95) -> dict:
	"""Return safety stock and reorder point given daily demand stats and lead time.

	Formulae:
	- safety_stock = z * sigma_daily * sqrt(lead_time)
	- reorder_point = mean * lead_time + safety_stock
	"""
	ss = compute_safety_stock(daily_std, float(lead_time_days), service_level)
	rp = compute_reorder_point(daily_mean, float(lead_time_days), ss)
	return {"safety_stock": float(np.ceil(ss)), "reorder_point": float(np.ceil(rp))}


def _optimize_reorder_quantity(expected_demand: float, safety_stock: float, current_stock: float, holding_cost_per_unit_per_day: float, stockout_cost_per_unit: float) -> float:
	"""Solve a simple LP to minimize holding + stockout with slack for unmet demand.

	Minimize: holding_cost_per_unit_per_day * q + stockout_cost_per_unit * s
	Subject to: current_stock + q + s >= expected_demand + safety_stock, q>=0, s>=0
	"""
	if pulp is None:
		needed = expected_demand + safety_stock - current_stock
		return float(max(0.0, np.ceil(needed)))
	# LP formulation
	prob = pulp.LpProblem("inventory_opt", pulp.LpMinimize)
	q = pulp.LpVariable("q", lowBound=0)
	s = pulp.LpVariable("s", lowBound=0)
	prob += holding_cost_per_unit_per_day * q + stockout_cost_per_unit * s
	prob += current_stock + q + s >= expected_demand + safety_stock
	prob.solve(pulp.PULP_CBC_CMD(msg=False))
	val = float(pulp.value(q))
	if not np.isfinite(val) or val < 0:
		val = 0.0
	return float(np.ceil(val))


def optimize_inventory_from_quantiles(daily_mean: float, daily_std: float, lead_time_days: int, service_level: float, forecast_quantiles: dict | None, current_stock: float = 0.0, holding_cost_per_unit_per_day: float = 0.01, stockout_cost_per_unit: float = 1.0) -> dict:
	"""Use forecast quantiles to compute expected demand in lead time and optimize reorder quantity.

	forecast_quantiles example: {"p10": [...], "p50": [...], "p90": [...]} in daily units.
	If missing or shorter than lead_time_days, we fall back to mean * lead_time.
	"""
	base = reorder_point_and_safety_stock(daily_mean, daily_std, lead_time_days, service_level)
	ss = float(base["safety_stock"])  # already ceiled
	if forecast_quantiles and isinstance(forecast_quantiles, dict) and "p50" in forecast_quantiles:
		p50 = forecast_quantiles.get("p50", [])
		# Expected demand over lead time
		expected_demand = float(np.sum(np.array(p50[:max(int(lead_time_days), 0)], dtype=float)))
	else:
		expected_demand = float(daily_mean * max(lead_time_days, 0))

	suggested_q = _optimize_reorder_quantity(
		expected_demand=expected_demand,
		safety_stock=ss,
		current_stock=float(current_stock),
		holding_cost_per_unit_per_day=float(holding_cost_per_unit_per_day),
		stockout_cost_per_unit=float(stockout_cost_per_unit),
	)
	return {
		"reorder_point": float(base["reorder_point"]),
		"safety_stock": float(ss),
		"suggested_reorder_quantity": float(suggested_q),
		"meta": {"used_pulp": pulp is not None}
	}
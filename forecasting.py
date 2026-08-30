import warnings
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any

# Prophet and fallback import handling
_prophet_import_error = None
try:
	from prophet import Prophet
except Exception as e:  # pragma: no cover - exercised in fallback test via mocking
	Prophet = None  # type: ignore
	_prophet_import_error = e

_neuralprophet_import_error = None
try:
	from neuralprophet import NeuralProphet
except Exception as e:  # pragma: no cover
	NeuralProphet = None  # type: ignore
	_neuralprophet_import_error = e

# LightGBM may not be present; we treat it as optional for ensemble
_lgbm_import_error = None
try:
	import lightgbm as lgb
except Exception as e:  # pragma: no cover
	lgb = None  # type: ignore
	_lgbm_import_error = e


def _fit_prophet_forecast(history_df: pd.DataFrame, horizon: int) -> pd.DataFrame:
	"""Fit Prophet and return forecast DataFrame with columns ds, yhat, yhat_lower, yhat_upper."""
	if Prophet is None:
		raise ImportError("prophet not available")
	# Use 80% interval for 10th and 90th percentiles
	model = Prophet(interval_width=0.8)
	model.fit(history_df)
	future = model.make_future_dataframe(periods=horizon, freq=_infer_freq(history_df['ds']))
	forecast = model.predict(future)
	return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(horizon)


def _fit_neuralprophet_forecast(history_df: pd.DataFrame, horizon: int) -> pd.DataFrame:
	"""Fit NeuralProphet and return a Prophet-like forecast DataFrame."""
	if NeuralProphet is None:
		raise ImportError("neuralprophet not available")
	model = NeuralProphet(quantiles=[0.1, 0.5, 0.9])
	model.fit(history_df, freq=_infer_freq(history_df['ds']))
	future = model.make_future_dataframe(history_df, periods=horizon)
	forecast = model.predict(future)
	# NeuralProphet quantile columns: yhat1, yhat1-0.1, yhat1-0.5, yhat1-0.9 in newer versions
	col_median = 'yhat1' if 'yhat1' in forecast.columns else 'yhat'
	col_10 = 'yhat1-0.1' if 'yhat1-0.1' in forecast.columns else None
	col_50 = 'yhat1-0.5' if 'yhat1-0.5' in forecast.columns else None
	col_90 = 'yhat1-0.9' if 'yhat1-0.9' in forecast.columns else None
	out = forecast[['ds']].copy()
	if col_10 and col_90 and col_50:
		out['yhat_lower'] = forecast[col_10]
		out['yhat'] = forecast[col_50]
		out['yhat_upper'] = forecast[col_90]
	else:
		# Fallback: use median from main column and symmetric band via residual std
		out['yhat'] = forecast[col_median]
		std = float(history_df['y'].std() or 0.0)
		out['yhat_lower'] = out['yhat'] - 1.28 * std
		out['yhat_upper'] = out['yhat'] + 1.28 * std
	return out.tail(horizon)


def _infer_freq(ds_series: pd.Series) -> str:
	"""Infer frequency string from datetime series; default to 'D'."""
	try:
		freq = pd.infer_freq(pd.to_datetime(ds_series))
		return freq or 'D'
	except Exception:
		return 'D'


def _prepare_history(history: List[List[Any]]) -> pd.DataFrame:
	"""Convert user history [[date, qty], ...] to DataFrame with columns ds, y."""
	df = pd.DataFrame(history, columns=['ds', 'y'])
	df['ds'] = pd.to_datetime(df['ds'])
	df['y'] = pd.to_numeric(df['y'], errors='coerce')
	df = df.dropna(subset=['ds', 'y']).sort_values('ds')
	return df


def _train_lgbm_lag_model(history_df: pd.DataFrame, max_lag: int = 30):
	"""Train a LightGBM regressor on lag features up to max_lag."""
	if lgb is None:
		raise ImportError("lightgbm not available")
	work = history_df.copy()
	work = work.set_index('ds').asfreq(_infer_freq(history_df['ds']))
	work['y'] = work['y'].interpolate(limit_direction='both')
	for lag in range(1, max_lag + 1):
		work[f'lag_{lag}'] = work['y'].shift(lag)
	work = work.dropna()
	X = work[[f'lag_{i}' for i in range(1, max_lag + 1)]]
	y = work['y']
	model = lgb.LGBMRegressor(n_estimators=500, learning_rate=0.05, max_depth=-1, subsample=0.8, colsample_bytree=0.8, random_state=42)
	model.fit(X, y)
	return model, work


def _predict_lgbm_iterative(model, history_df: pd.DataFrame, horizon: int, max_lag: int = 30) -> Tuple[pd.DatetimeIndex, np.ndarray]:
	"""Iteratively forecast horizon steps using the trained LGBM with rolling lags."""
	freq = _infer_freq(history_df['ds'])
	idx = pd.DatetimeIndex(history_df['ds']).sort_values()
	series = pd.Series(history_df['y'].values, index=idx)
	series = series.asfreq(freq)
	series = series.interpolate(limit_direction='both')
	preds: List[float] = []
	current_index = series.index
	for step in range(horizon):
		last_values = series.iloc[-max_lag:]
		if len(last_values) < max_lag:
			pad = np.repeat(last_values.iloc[0], max_lag - len(last_values))
			features = np.concatenate([pad, last_values.values])
		else:
			features = last_values.values
		X = features[::-1].reshape(1, -1)  # latest as lag_1
		pred = float(model.predict(X)[0])
		preds.append(pred)
		next_ts = (current_index[-1] + pd.tseries.frequencies.to_offset(freq)) if len(current_index) else pd.Timestamp(series.index[-1])
		current_index = current_index.append(pd.DatetimeIndex([next_ts]))
		series = pd.concat([series, pd.Series([pred], index=pd.DatetimeIndex([next_ts]))])
	future_idx = current_index[-horizon:]
	return future_idx, np.array(preds)


def get_probabilistic_forecast(history: List[List[Any]], horizon: int, use_ensemble: bool = True) -> Dict[str, Any]:
	"""
	Compute probabilistic demand forecast.

	Args:
		history: List of [date, quantity]. Date can be string or datetime-like.
		horizon: Number of future periods to forecast.
		use_ensemble: If True, average Prophet/NeuralProphet median with LightGBM point forecast when LightGBM is available.

	Returns:
		Dictionary with keys: dates (ISO strings), p10, p50, p90, median (alias of p50), meta.
	"""
	if horizon <= 0:
		raise ValueError("horizon must be > 0")
	hist_df = _prepare_history(history)
	if hist_df.empty:
		raise ValueError("history has no valid rows")

	# Baseline forecast via Prophet, fallback to NeuralProphet
	forecast_df = None
	baseline_model = 'prophet'
	try:
		forecast_df = _fit_prophet_forecast(hist_df, horizon)
	except Exception:
		baseline_model = 'neuralprophet'
		forecast_df = _fit_neuralprophet_forecast(hist_df, horizon)

	# LightGBM ensemble (median only); use Prophet quantiles for p10/p90
	ensemble_used = False
	lgbm_preds = None
	if use_ensemble:
		try:
			model, _ = _train_lgbm_lag_model(hist_df, max_lag=30)
			future_idx, lgbm_preds = _predict_lgbm_iterative(model, hist_df, horizon, max_lag=30)
			# Align order with forecast_df
			ensemble_used = True
		except Exception:
			ensemble_used = False

	# Build outputs
	dates = pd.to_datetime(forecast_df['ds']).dt.strftime('%Y-%m-%d').tolist()
	p50 = forecast_df['yhat'].astype(float).values
	p10 = forecast_df['yhat_lower'].astype(float).values
	p90 = forecast_df['yhat_upper'].astype(float).values
	if ensemble_used and lgbm_preds is not None:
		# Average p50 with deterministic lgbm point forecast
		p50 = (p50 + lgbm_preds) / 2.0

	result = {
		"dates": dates,
		"p10": [float(x) for x in p10],
		"p50": [float(x) for x in p50],
		"p90": [float(x) for x in p90],
		"median": [float(x) for x in p50],
		"meta": {
			"baseline_model": baseline_model,
			"ensemble_used": bool(ensemble_used),
			"warnings": _collect_warnings()
		}
	}
	return result


def _collect_warnings() -> List[str]:
	msgs: List[str] = []
	if _prophet_import_error is not None:
		msgs.append("prophet_import_error")
	if _neuralprophet_import_error is not None:
		msgs.append("neuralprophet_import_error")
	if _lgbm_import_error is not None:
		msgs.append("lightgbm_import_error")
	return msgs
import os
import sys
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import pandas as pd
from io import BytesIO
from .auth import get_current_user

# Ensure repository root is on sys.path so we can import existing modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from forecasting import get_probabilistic_forecast
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

_shap_import_error = None
try:
    import shap
except Exception as e:  # pragma: no cover
    shap = None  # type: ignore
    _shap_import_error = e

_lgbm_import_error = None
try:
    import lightgbm as lgb
except Exception as e:  # pragma: no cover
    lgb = None  # type: ignore
    _lgbm_import_error = e

_prophet_avail = True
try:
    from prophet import Prophet
except Exception:
    _prophet_avail = False

# MLflow optional
_mlflow_error = None
try:
    import mlflow
    from .mlflow_config import configure_mlflow
except Exception as e:  # pragma: no cover
    mlflow = None  # type: ignore
    _mlflow_error = e
from risk import train_and_score
from inventory import InventoryParams, recommend_inventory
from .monitoring import check_and_log_drift

router = APIRouter()

@router.post("/forecast")
async def api_forecast(file: UploadFile = File(...), product: str = Form(None), periods: int = Form(12), user=Depends(get_current_user)):
    try:
        content = await file.read()
        buf = BytesIO(content)
        df = pd.read_csv(buf) if file.filename.endswith('.csv') else pd.read_excel(buf)

        # Handle both wide format (with Product column) and long format
        date_col = None
        qty_col = None

        # Check for standard column names
        for c in df.columns:
            lc = c.lower()
            if date_col is None and lc in ("date", "ds", "timestamp"):
                date_col = c
            if qty_col is None and lc in ("sales", "qty", "quantity", "y", "demand"):
                qty_col = c

        # If product is specified and we have the required columns, filter the data
        if product is not None and 'Product' in df.columns and date_col and qty_col:
            df = df[df['Product'] == product]

        if date_col is None or qty_col is None:
            raise HTTPException(status_code=400, detail="Input must contain date and quantity columns")

        # Convert to list of [date, qty] pairs
        history = df[[date_col, qty_col]].values.tolist()

        # Monitoring drift: compare last 30 vs last 10 points
        try:
            incoming_vals = pd.to_numeric(df[qty_col], errors='coerce').dropna().tolist()[-10:]
            train_vals = pd.to_numeric(df[qty_col], errors='coerce').dropna().tolist()[-30:]
            check_and_log_drift("/ml/forecast", train_vals, incoming_vals)
        except Exception as e:
            print(f"Monitoring error: {e}")

        # Get the forecast
        try:
            res = get_probabilistic_forecast(history, periods, use_ensemble=False)
        except Exception as forecast_error:
            print(f"Forecast error: {forecast_error}")
            # Return simple fallback forecast
            import datetime
            dates = [(datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, periods + 1)]
            median_val = float(df[qty_col].mean()) if qty_col in df.columns else 100
            res = {
                "dates": dates,
                "p10": [median_val * 0.8] * periods,
                "p50": [median_val] * periods,
                "p90": [median_val * 1.2] * periods,
                "median": [median_val] * periods,
                "meta": {
                    "baseline_model": "fallback",
                    "ensemble_used": False,
                    "warnings": [str(forecast_error)]
                }
            }
        return res
    except HTTPException:
        raise
    except Exception as e:
        print(f"API Forecast error: {e}")
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


def _infer_freq(ds_series: pd.Series) -> str:
    try:
        freq = pd.infer_freq(pd.to_datetime(ds_series))
        return freq or 'D'
    except Exception:
        return 'D'


def _prepare_history_two_col(df: pd.DataFrame) -> pd.DataFrame:
    date_col = None
    qty_col = None
    for c in df.columns:
        lc = c.lower()
        if date_col is None and lc in ("date", "ds", "timestamp"):
            date_col = c
        if qty_col is None and lc in ("sales", "qty", "quantity", "y", "demand"):
            qty_col = c
    if date_col is None or qty_col is None:
        raise HTTPException(status_code=400, detail="Input must contain date and quantity columns")
    hist = df[[date_col, qty_col]].copy()
    hist.columns = ["ds", "y"]
    hist["ds"] = pd.to_datetime(hist["ds"])
    hist["y"] = pd.to_numeric(hist["y"], errors='coerce')
    hist = hist.dropna().sort_values("ds")
    return hist


def explain_forecast_lightgbm(history_df: pd.DataFrame, max_lag: int = 30, top_k: int = 5) -> dict:
    if lgb is None or shap is None:
        return {"contributors": []}
    work = history_df.set_index('ds').asfreq(_infer_freq(history_df['ds']))
    work['y'] = work['y'].interpolate(limit_direction='both')
    for lag in range(1, max_lag + 1):
        work[f'lag_{lag}'] = work['y'].shift(lag)
    work = work.dropna()
    if work.empty:
        return {"contributors": []}
    X = work[[f'lag_{i}' for i in range(1, max_lag + 1)]]
    y = work['y']
    model = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, random_state=42)
    model.fit(X, y)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    if isinstance(shap_values, list):
        shap_values = shap_values[0]
    abs_vals = np.mean(np.abs(shap_values), axis=0)
    order = np.argsort(-abs_vals)[:top_k]
    contributors = [{"feature": X.columns[i], "importance": float(abs_vals[i])} for i in order]
    return {"contributors": contributors}


def explain_forecast_prophet(history_df: pd.DataFrame, horizon: int = 14, top_k: int = 5) -> dict:
    if not _prophet_avail:
        return {"contributors": []}
    model = Prophet()
    model.fit(history_df.rename(columns={"ds": "ds", "y": "y"}))
    future = model.make_future_dataframe(periods=horizon, freq=_infer_freq(history_df['ds']))
    forecast = model.predict(future)
    components = {}
    for comp in [c for c in forecast.columns if c in ("trend", "weekly", "yearly", "daily") or c.endswith("_additive") or c.endswith("_multiplicative")]:
        components[comp] = float(np.std(forecast[comp].values))
    if "trend" not in components and "trend" in forecast.columns:
        components["trend"] = float(np.std(forecast["trend"].values))
    order_pairs = sorted(components.items(), key=lambda x: -abs(x[1]))[:top_k]
    contributors = [{"feature": k, "importance": float(abs(v))} for k, v in order_pairs]
    return {"contributors": contributors}


def generate_contrib_bar_plot(contributors: list) -> str:
    if not contributors:
        return ""
    labels = [c["feature"] for c in contributors]
    vals = [c["importance"] for c in contributors]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(labels[::-1], vals[::-1])
    ax.set_xlabel("importance")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


@router.post("/forecast_explain")
async def api_forecast_explain(file: UploadFile = File(...), periods: int = Form(14), model: str = Form("auto"), user=Depends(get_current_user)):
    content = await file.read()
    buf = BytesIO(content)
    df = pd.read_csv(buf) if file.filename.endswith('.csv') else pd.read_excel(buf)
    hist = _prepare_history_two_col(df)
    result = {"contributors": []}
    if model in ("auto", "lgbm"):
        lg = explain_forecast_lightgbm(hist)
        if lg["contributors"]:
            result = lg
    if (not result["contributors"]) and model in ("auto", "prophet"):
        pp = explain_forecast_prophet(hist, horizon=periods)
        result = pp
    result["plot_png_base64"] = generate_contrib_bar_plot(result.get("contributors", []))
    return result


@router.post("/forecast_prob")
async def api_forecast_prob(file: UploadFile = File(...), periods: int = Form(12), user=Depends(get_current_user)):
    content = await file.read()
    buf = BytesIO(content)
    df = pd.read_csv(buf) if file.filename.endswith('.csv') else pd.read_excel(buf)
    # Expect two columns: date and qty-like
    date_col = None
    qty_col = None
    for c in df.columns:
        lc = c.lower()
        if date_col is None and lc in ("date", "ds", "timestamp"):
            date_col = c
        if qty_col is None and lc in ("sales", "qty", "quantity", "y", "demand"):
            qty_col = c
    if date_col is None or qty_col is None:
        raise HTTPException(status_code=400, detail="Input must contain date and quantity columns")
    history = df[[date_col, qty_col]].values.tolist()
    try:
        incoming_vals = pd.to_numeric(df[qty_col], errors='coerce').dropna().tolist()[-10:]
        train_vals = pd.to_numeric(df[qty_col], errors='coerce').dropna().tolist()[-30:]
        check_and_log_drift("/ml/forecast_prob", train_vals, incoming_vals)
    except Exception:
        pass
    res = get_probabilistic_forecast(history, periods, use_ensemble=True)
    # Log simple metrics if actuals included in uploaded data
    try:
        if mlflow is not None:
            exp = configure_mlflow()
            with mlflow.start_run(run_name="forecast_prob", experiment_id=mlflow.get_experiment_by_name(exp).experiment_id):
                mlflow.log_param("model_type", "prophet+lgbm_ensemble")
                mlflow.log_param("horizon", int(periods))
                # If history has 'y' and we can compute in-sample last N as naive metric placeholders
                import numpy as np
                p50 = np.array(res.get("p50", []), dtype=float)
                # No ground truth for future; skip unless uploaded contains overlap
                mae = float(np.nan)
                rmse = float(np.nan)
                mlflow.log_metric("mae", mae)
                mlflow.log_metric("rmse", rmse)
                # Save forecast as artifact
                import json, os
                out_path = os.path.join(os.path.dirname(__file__), "..", "models", "forecast_last.json")
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(res, f, indent=2)
    except Exception as e:
        print(f"MLflow logging error: {e}")
    return res


@router.post("/risk")
async def api_risk(file: UploadFile = File(...), target: str = Form("label"), model: str = Form("rf"), user=Depends(get_current_user)):
    try:
        content = await file.read()
        buf = BytesIO(content)
        df = pd.read_csv(buf) if file.filename.endswith('.csv') else pd.read_excel(buf)
        _, metrics, scored = train_and_score(df, target, model)
        metrics.pop("probas", None)
        return {"metrics": metrics, "scores": scored.to_dict(orient="records")}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Risk analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.post("/inventory")
async def api_inventory(file: UploadFile = File(...), service_level: float = Form(0.95), lead_time_days: int = Form(14), holding_cost: float = Form(2.0), ordering_cost: float = Form(50.0), user=Depends(get_current_user)):
    content = await file.read()
    buf = BytesIO(content)
    df = pd.read_csv(buf) if file.filename.endswith('.csv') else pd.read_excel(buf)
    params = InventoryParams(service_level=service_level, lead_time_days=lead_time_days, holding_cost_per_unit_per_year=holding_cost, ordering_cost_per_order=ordering_cost)
    res = recommend_inventory(df, params)
    return {"recommendations": res.to_dict(orient="records")}
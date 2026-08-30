import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

try:
	from xgboost import XGBClassifier
	HAS_XGB = True
except Exception:
	HAS_XGB = False


def split_features_labels(df: pd.DataFrame, target_column: str):
	X = df.drop(columns=[target_column])
	y = df[target_column]
	return X, y


def build_model(model_name: str, random_state: int = 42):
	model_name = model_name.lower()
	if model_name in ["logreg", "logistic", "logistic_regression"]:
		return LogisticRegression(max_iter=1000, solver="liblinear", class_weight="balanced", random_state=random_state)
	elif model_name in ["rf", "randomforest", "random_forest"]:
		return RandomForestClassifier(n_estimators=300, max_depth=None, n_jobs=-1, class_weight="balanced_subsample", random_state=random_state)
	elif model_name in ["xgb", "xgboost"] and HAS_XGB:
		return XGBClassifier(
			n_estimators=400,
			learning_rate=0.05,
			max_depth=6,
			subsample=0.9,
			colsample_bytree=0.9,
			reg_lambda=1.0,
			objective="binary:logistic",
			random_state=random_state,
			n_jobs=-1,
			verbosity=0
		)
	else:
		raise ValueError("Unsupported model or XGBoost not installed.")


def evaluate_classifier(model, X_test: pd.DataFrame, y_test: pd.Series):
	probas = None
	if hasattr(model, "predict_proba"):
		probas = model.predict_proba(X_test)[:, 1]
	y_pred = model.predict(X_test)
	precision = precision_score(y_test, y_pred, zero_division=0)
	recall = recall_score(y_test, y_pred, zero_division=0)
	f1 = f1_score(y_test, y_pred, zero_division=0)
	report = classification_report(y_test, y_pred, zero_division=0, output_dict=True)
	return {
		"precision": precision,
		"recall": recall,
		"f1": f1,
		"report": report,
		"probas": probas
	}


def _clean_target(df: pd.DataFrame, target_column: str) -> pd.DataFrame:
	# Drop rows where target is NaN
	df_clean = df.dropna(subset=[target_column]).copy()
	# Coerce target to numeric 0/1 where possible
	try:
		df_clean[target_column] = pd.to_numeric(df_clean[target_column])
	except Exception:
		pass
	# Map common strings to 0/1
	mapping = {"yes": 1, "y": 1, "true": 1, "t": 1, "issue": 1, "delay": 1,
			   "no": 0, "n": 0, "false": 0, "f": 0, "normal": 0}
	if df_clean[target_column].dtype == object:
		df_clean[target_column] = df_clean[target_column].str.lower().map(mapping)
	# Ensure binary labels
	unique_vals = pd.Series(df_clean[target_column].unique()).dropna().sort_values().tolist()
	if not set(unique_vals).issubset({0, 1}):
		raise ValueError(f"Target column '{target_column}' must be binary (0/1). Found values: {unique_vals}")
	return df_clean


def train_and_score(df: pd.DataFrame, target_column: str, model_name: str):
	df_proc = df.copy()
	numeric_cols = df_proc.select_dtypes(include=[np.number]).columns.tolist()
	if target_column not in df_proc.columns:
		raise ValueError(f"Target column '{target_column}' not in dataframe")

	# Keep numeric features + target
	keep_cols = [c for c in numeric_cols if c != target_column] + [target_column]
	df_proc = df_proc[keep_cols]

	# Fill numeric missing values
	for col in keep_cols:
		if col != target_column and df_proc[col].isna().any():
			df_proc[col] = df_proc[col].fillna(df_proc[col].median())

	# Clean target, drop NaNs and enforce binary
	df_proc = _clean_target(df_proc, target_column)

	X, y = split_features_labels(df_proc, target_column)

	# Ensure both classes exist after cleaning
	if y.nunique() < 2:
		raise ValueError("Target column must contain at least two classes after cleaning.")

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

	scaler = None
	if model_name.lower() in ["logreg", "logistic", "logistic_regression"]:
		scaler = StandardScaler()
		X_train = scaler.fit_transform(X_train)
		X_test = scaler.transform(X_test)

	model = build_model(model_name)
	model.fit(X_train, y_train)
	metrics = evaluate_classifier(model, X_test, y_test)

	# Risk scores for all rows (probability of issue)
	if hasattr(model, "predict_proba"):
		all_scores = model.predict_proba(X if scaler is None else scaler.transform(X))[:, 1]
	else:
		if hasattr(model, "decision_function"):
			vals = model.decision_function(X if scaler is None else scaler.transform(X))
			vals = (vals - vals.min()) / (vals.max() - vals.min() + 1e-9)
			all_scores = vals
		else:
			all_scores = model.predict(X if scaler is None else scaler.transform(X)).astype(float)

	risk_df = df.copy()
	risk_df["risk_score"] = np.nan
	risk_df.loc[df_proc.index, "risk_score"] = all_scores

	return model, metrics, risk_df
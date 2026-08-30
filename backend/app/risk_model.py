import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from typing import Dict, Any, Tuple
import joblib
import os

class SupplyChainRiskModel:
    """Advanced risk prediction model for supply chain management"""

    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_names = None

        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
        elif model_type == "logistic_regression":
            self.model = LogisticRegression(
                random_state=42,
                class_weight='balanced',
                max_iter=1000
            )
        else:
            raise ValueError("Unsupported model type")

    def preprocess_data(self, df: pd.DataFrame, target_column: str = "Risk_Label") -> Tuple[pd.DataFrame, pd.Series]:
        """Preprocess the input data for training/prediction"""

        # Select numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_column in numeric_cols:
            numeric_cols.remove(target_column)

        # Keep only numeric features + target
        features = df[numeric_cols].copy()
        target = df[target_column].copy()

        # Handle missing values
        features = features.fillna(features.median())

        # Store feature names
        self.feature_names = features.columns.tolist()

        return features, target

    def train(self, df: pd.DataFrame, target_column: str = "Risk_Label", test_size: float = 0.2) -> Dict[str, Any]:
        """Train the risk prediction model"""

        # Preprocess data
        X, y = self.preprocess_data(df, target_column)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Scale features for logistic regression
        if self.model_type == "logistic_regression":
            self.scaler = StandardScaler()
            X_train = self.scaler.fit_transform(X_train)
            X_test = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train, y_train)

        # Make predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        report = classification_report(y_test, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y_test, y_pred)

        # Feature importance (for Random Forest)
        feature_importance = None
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))

        return {
            "accuracy": report['accuracy'],
            "precision": report['weighted avg']['precision'],
            "recall": report['weighted avg']['recall'],
            "f1_score": report['weighted avg']['f1-score'],
            "confusion_matrix": conf_matrix.tolist(),
            "feature_importance": feature_importance,
            "model_type": self.model_type
        }

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Make predictions on new data"""

        # Preprocess data
        X, _ = self.preprocess_data(df)

        # Scale features if needed
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X

        # Make predictions
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]

        # Create results dataframe
        results = df.copy()
        results['risk_prediction'] = predictions
        results['risk_probability'] = probabilities

        # Add risk level
        results['risk_level'] = results['risk_probability'].apply(self._classify_risk_level)

        return results

    def _classify_risk_level(self, probability: float) -> str:
        """Classify risk level based on probability"""
        if probability >= 0.8:
            return "Critical"
        elif probability >= 0.6:
            return "High"
        elif probability >= 0.4:
            return "Medium"
        elif probability >= 0.2:
            return "Low"
        else:
            return "Minimal"

    def save_model(self, filepath: str):
        """Save the trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }
        joblib.dump(model_data, filepath)

    def load_model(self, filepath: str):
        """Load a trained model"""
        if os.path.exists(filepath):
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.model_type = model_data['model_type']
            return True
        return False

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance if available"""
        if hasattr(self.model, 'feature_importances_'):
            return dict(zip(self.feature_names, self.model.feature_importances_))
        elif hasattr(self.model, 'coef_'):
            # For logistic regression
            importance = np.abs(self.model.coef_[0])
            return dict(zip(self.feature_names, importance))
        else:
            return {}

def create_risk_assessment_report(predictions_df: pd.DataFrame) -> Dict[str, Any]:
    """Create a comprehensive risk assessment report"""

    # Overall statistics
    total_products = len(predictions_df)
    high_risk_count = len(predictions_df[predictions_df['risk_level'].isin(['Critical', 'High'])])
    medium_risk_count = len(predictions_df[predictions_df['risk_level'] == 'Medium'])
    low_risk_count = len(predictions_df[predictions_df['risk_level'].isin(['Low', 'Minimal'])])

    # Risk distribution
    risk_distribution = predictions_df['risk_level'].value_counts().to_dict()

    # Average risk probability
    avg_risk_prob = predictions_df['risk_probability'].mean()

    # Top risk factors (if available)
    top_risk_products = predictions_df.nlargest(10, 'risk_probability')[['Product', 'risk_probability', 'risk_level']]

    return {
        "summary": {
            "total_products": total_products,
            "high_risk_products": high_risk_count,
            "medium_risk_products": medium_risk_count,
            "low_risk_products": low_risk_count,
            "average_risk_probability": avg_risk_prob,
            "risk_distribution": risk_distribution
        },
        "top_risk_products": top_risk_products.to_dict('records'),
        "recommendations": generate_risk_recommendations(risk_distribution)
    }

def generate_risk_recommendations(risk_distribution: Dict[str, int]) -> List[str]:
    """Generate risk mitigation recommendations based on risk distribution"""

    recommendations = []

    if risk_distribution.get('Critical', 0) > 0:
        recommendations.append("🚨 IMMEDIATE ACTION: Address critical risk products - consider alternative suppliers or expedited shipping")

    if risk_distribution.get('High', 0) > 0:
        recommendations.append("⚠️ HIGH PRIORITY: Review high-risk products - implement safety stock and supplier monitoring")

    if risk_distribution.get('Medium', 0) > 0:
        recommendations.append("📊 MONITOR: Medium-risk products require regular monitoring and contingency planning")

    if risk_distribution.get('Low', 0) > 0 or risk_distribution.get('Minimal', 0) > 0:
        recommendations.append("✅ STABLE: Low-risk products are well-managed, maintain current strategies")

    recommendations.append("🔄 GENERAL: Implement automated monitoring system for continuous risk assessment")
    recommendations.append("📈 IMPROVEMENT: Consider supplier diversification and inventory optimization strategies")

    return recommendations
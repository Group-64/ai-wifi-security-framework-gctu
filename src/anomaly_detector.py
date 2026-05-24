"""
GCTU WiFi Security Framework - Anomaly Detection Module
Implements Isolation Forest for unsupervised anomaly detection
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import os

class AnomalyDetector:
    """
    Anomaly detection class using Isolation Forest algorithm.
    """

    def __init__(self, contamination=0.1, random_state=42):
        """
        Initialise the anomaly detector.

        Parameters:
        -----------
        contamination : float
            Expected proportion of anomalies in the dataset (0.0 to 0.5)
        random_state : int
            Seed for reproducible results
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.feature_columns = ['signal_rssi', 'data_up_mb', 'data_down_mb', 'duration_sec']
        self.is_fitted = False

    def preprocess_features(self, df):
        """
        Extract and preprocess features for anomaly detection.

        Parameters:
        -----------
        df : pd.DataFrame
            Raw WiFi data

        Returns:
        --------
        np.ndarray
            Preprocessed feature matrix
        """
        # Check if all required columns exist
        missing_cols = [col for col in self.feature_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")

        # Extract features
        X = df[self.feature_columns].copy()

        # Handle missing values
        X = X.fillna(X.median())

        # Remove infinite values
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())

        return X

    def train(self, df):
        """
        Train the Isolation Forest model.

        Parameters:
        -----------
        df : pd.DataFrame
            Training data

        Returns:
        --------
        self
        """
        print("[INFO] Preprocessing training features...")
        X = self.preprocess_features(df)

        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        print("[INFO] Training Isolation Forest model...")
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=self.random_state,
            bootstrap=False
        )
        self.model.fit(X_scaled)
        self.is_fitted = True

        print(f"[INFO] Training complete. Model trained on {X_scaled.shape[0]} samples.")

        return self

    def predict(self, df):
        """
        Predict anomalies in new data.

        Parameters:
        -----------
        df : pd.DataFrame
            Data to evaluate

        Returns:
        --------
        pd.DataFrame
            Original data with anomaly predictions added
        """
        if not self.is_fitted:
            raise ValueError("Model has not been trained. Call train() first.")

        # Preprocess features
        X = self.preprocess_features(df)
        X_scaled = self.scaler.transform(X)

        # Predict (-1 = anomaly, 1 = normal)
        predictions = self.model.predict(X_scaled)

        # Get anomaly scores (lower = more anomalous)
        scores = self.model.score_samples(X_scaled)

        # Add predictions to dataframe
        result_df = df.copy()
        result_df['anomaly_prediction'] = predictions
        result_df['anomaly_score'] = scores
        result_df['is_predicted_anomaly'] = (predictions == -1).astype(int)

        return result_df

    def evaluate(self, df_true, df_pred):
        """
        Evaluate detection performance against ground truth labels.

        Parameters:
        -----------
        df_true : pd.DataFrame
            Data with true labels ('is_anomaly' column)
        df_pred : pd.DataFrame
            Data with predicted labels ('is_predicted_anomaly' column)

        Returns:
        --------
        dict
            Evaluation metrics
        """
        y_true = df_true['is_anomaly'].values
        y_pred = df_pred['is_predicted_anomaly'].values

        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_true, y_pred)
        }

        return metrics

    def save_model(self, filepath="models/isolation_forest.pkl"):
        """Save trained model and scaler to disk."""
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, filepath)
        joblib.dump(self.scaler, filepath.replace('.pkl', '_scaler.pkl'))
        print(f"[INFO] Model saved to {filepath}")
        print(f"[INFO] Scaler saved to {filepath.replace('.pkl', '_scaler.pkl')}")

    def load_model(self, filepath="models/isolation_forest.pkl"):
        """Load trained model and scaler from disk."""
        self.model = joblib.load(filepath)
        self.scaler = joblib.load(filepath.replace('.pkl', '_scaler.pkl'))
        self.is_fitted = True
        print(f"[INFO] Model loaded from {filepath}")
        return self


# For testing the module directly
if __name__ == "__main__":
    print("=" * 50)
    print("GCTU WiFi Security Framework - Anomaly Detection Module")
    print("=" * 50)
    print("AnomalyDetector class is ready to use.")
    print("\nExample usage:")
    print("  detector = AnomalyDetector(contamination=0.1)")
    print("  detector.train(df)")
    print("  results = detector.predict(df)")
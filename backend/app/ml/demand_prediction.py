import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pickle
import os

class DemandPredictor:
    def __init__(self, n_clusters=20):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            objective='reg:squarederror'
        )
        self.cluster_centers = None

    def fit_clusters(self, df):
        """Perform spatial clustering on EMS events."""
        print("Fitting clusters...")
        coords = df[['lat', 'lon']]
        self.kmeans.fit(coords)
        self.cluster_centers = self.kmeans.cluster_centers_
        df['cluster'] = self.kmeans.predict(coords)
        return df

    def prepare_training_data(self, df):
        """Prepare data for XGBoost prediction."""
        print("Preparing training data...")
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        
        # Group by cluster, hour, and day_of_week to get demand counts
        demand_counts = df.groupby(['cluster', 'hour', 'day_of_week']).size().reset_index(name='demand')
        
        # Fill missing combinations with 0
        all_clusters = range(self.n_clusters)
        all_hours = range(24)
        all_days = range(7)
        
        index = pd.MultiIndex.from_product([all_clusters, all_hours, all_days], 
                                          names=['cluster', 'hour', 'day_of_week'])
        full_df = pd.DataFrame(index=index).reset_index()
        
        training_data = pd.merge(full_df, demand_counts, on=['cluster', 'hour', 'day_of_week'], how='left').fillna(0)
        return training_data

    def train(self, training_data):
        """Train the XGBoost model."""
        print("Training XGBoost model...")
        X = training_data[['cluster', 'hour', 'day_of_week']]
        y = training_data['demand']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        print(f"Model trained. RMSE: {rmse}")

    def predict(self, cluster, hour, day_of_week):
        """Predict demand for a given cluster and time."""
        X = pd.DataFrame([[cluster, hour, day_of_week]], columns=['cluster', 'hour', 'day_of_week'])
        return max(0, self.model.predict(X)[0])

    def save_model(self, path="data/processed/"):
        """Save the trained models."""
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "kmeans.pkl"), "wb") as f:
            pickle.dump(self.kmeans, f)
        self.model.save_model(os.path.join(path, "xgboost_model.json"))
        print(f"Models saved to {path}")

    def load_model(self, path="data/processed/"):
        """Load the trained models."""
        with open(os.path.join(path, "kmeans.pkl"), "rb") as f:
            self.kmeans = pickle.load(f)
        self.model.load_model(os.path.join(path, "xgboost_model.json"))
        self.cluster_centers = self.kmeans.cluster_centers_
        print(f"Models loaded from {path}")

if __name__ == "__main__":
    # Example usage
    try:
        df = pd.read_csv("data/raw/historical_ems.csv")
        predictor = DemandPredictor()
        df = predictor.fit_clusters(df)
        training_data = predictor.prepare_training_data(df)
        predictor.train(training_data)
        predictor.save_model()
    except FileNotFoundError:
        print("Historical EMS data not found. Please run ingestion script first.")

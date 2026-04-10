import os
import io
import base64
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_pre_training():
    dataset_path = os.path.join(BASE_DIR, 'media', 'wind_power_dataset_50000.csv')
    models_dir = os.path.join(BASE_DIR, 'models')
    os.makedirs(models_dir, exist_ok=True)

    print("Loading dataset...")
    df = pd.read_csv(dataset_path)

    if 'Timestamp' in df.columns:
        df = df.drop(columns=['Timestamp'])

    X = df.drop(columns=['Active_Wind_Power_kW'])
    y = df['Active_Wind_Power_kW']

    print("Splitting and scaling...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        'Linear Regression': LinearRegression(),
        'Lasso Regression': Lasso(),
        'SVR (Support Vector)': SVR(),
        'KNN Regressor': KNeighborsRegressor(n_neighbors=5)
    }

    comparison_results = []
    best_model_name = ""
    best_model = None
    best_r2 = -float('inf')
    best_metrics = {}

    print("Training models...")
    for name, m in models.items():
        print(f"Training {name}...")
        m.fit(X_train_scaled, y_train)
        y_pred = m.predict(X_test_scaled)
        
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        
        comparison_results.append({
            'model_name': name,
            'accuracy_r2': round(r2, 4),
            'mae': round(mae, 2),
            'rmse': round(rmse, 2)
        })
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = m
            best_model_name = name
            best_metrics = {'mae': mae, 'mse': mse, 'rmse': rmse, 'r2': r2}

    print("Saving models and metrics...")
    joblib.dump(best_model, os.path.join(models_dir, 'model.pkl'))
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
    with open(os.path.join(models_dir, 'model_name.txt'), 'w') as f:
        f.write(best_model_name)

    metrics_data = {
        'best_model_name': best_model_name,
        'mae': f"{best_metrics['mae']:.2f}",
        'mse': f"{best_metrics['mse']:.2f}",
        'rmse': f"{best_metrics['rmse']:.2f}",
        'r2': f"{best_metrics['r2']:.4f}",
        'comparison_results': comparison_results
    }
    
    with open(os.path.join(models_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics_data, f)

    print("Generating correlation matrix...")
    corr = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True)
    plt.title("Correlation Matrix")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()
    
    with open(os.path.join(models_dir, 'correlation_plot.txt'), 'w') as f:
        f.write(image_base64)

    print("Pre-training completed successfully!")

if __name__ == "__main__":
    run_pre_training()

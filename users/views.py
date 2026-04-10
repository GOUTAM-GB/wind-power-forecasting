from django.conf import settings
from django.shortcuts import render, redirect
import pandas as pd

from users.forms import WindInputForm
from .models import UserRegistrationModel
from django.contrib import messages
import re

def UserRegisterActions(request):
    if request.method == 'POST':

        name = request.POST.get('name')
        loginid = request.POST.get('loginid')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        locality = request.POST.get('locality')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')

        # -----------------------------
        # VALIDATIONS
        # -----------------------------

        # 1. Mobile validation (Indian)
        if not re.match(r'^[6-9][0-9]{9}$', mobile):
            messages.error(request, "Invalid mobile number. Must be 10 digits and start with 6-9.")
            return render(request, 'UserRegistrations.html')

        # 2. Password validation
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%?&]).{8,}$', password):
            print("my password is",password)
            print("password must have 1 capital letter, 1 number, 1 special symbol, and be at least 8 characters long.")
            messages.error(request, "Password must have 1 capital letter, 1 number, 1 special symbol, and be at least 8 characters long.")
            return render(request, 'UserRegistrations.html')

        # 3. Check duplicate login ID
        if UserRegistrationModel.objects.filter(loginid=loginid).exists():
            messages.error(request, "Login ID already taken. Try another.")
            return render(request, 'UserRegistrations.html')

        # 4. Check duplicate mobile
        if UserRegistrationModel.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return render(request, 'UserRegistrations.html')

        # 5. Check duplicate email
        if UserRegistrationModel.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'UserRegistrations.html')

        # -----------------------------
        # SAVE DATA
        # -----------------------------
        UserRegistrationModel.objects.create(
            name=name,
            loginid=loginid,
            password=password,
            mobile=mobile,
            email=email,
            locality=locality,
            address=address,
            city=city,
            state=state,
            status='waiting'
        )

        messages.success(request, "Registration successful!")
    return render(request, 'UserRegistrations.html')


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                data = {'loginid': loginid}
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})


def index(request):
    return render(request,"index.html")

def logout_view(request):    
    return render(request, 'index.html')
import os
import io
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from django.shortcuts import render
from django.conf import settings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Move BASE_DIR definition to module level
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def train_view(request):
    try:
        # Set paths
        dataset_path = os.path.join(BASE_DIR, 'media', 'wind_power_dataset_50000.csv')
        models_dir = os.path.join(BASE_DIR, 'models')
        os.makedirs(models_dir, exist_ok=True)

        # Load dataset
        df = pd.read_csv(dataset_path)
        print(f"Dataset loaded successfully with {len(df)} rows")

        # Drop datetime or non-numeric columns if any
        if 'Timestamp' in df.columns:
            df = df.drop(columns=['Timestamp'])

        # Ensure only numeric columns are used
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if "Active_Wind_Power_kW" not in numeric_cols:
            raise ValueError("Target column 'Active_Wind_Power_kW' not found in numeric columns.")

        X = df.drop(columns=['Active_Wind_Power_kW'])
        y = df['Active_Wind_Power_kW']

        # Split dataset
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Feature scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Initialize models for comparison
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

        # Train and compare models
        print("Training models for comparison...")
        for name, m in models.items():
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
            
            # Select best model based on R2 Score
            if r2 > best_r2:
                best_r2 = r2
                best_model = m
                best_model_name = name
                best_metrics = {'mae': mae, 'mse': mse, 'rmse': rmse, 'r2': r2}

        # Print comparison nicely to terminal
        print("\n--- MODEL COMPARISON RESULTS ---")
        for res in comparison_results:
            print(f"Model: {res['model_name']} | Accuracy (R2): {res['accuracy_r2']} | RMSE: {res['rmse']}")
        print(f"=================================")
        print(f"Best Model Selected: {best_model_name} with Accuracy {round(best_r2, 4)}\n")

        # Save best model, scaler, and the model name
        joblib.dump(best_model, os.path.join(models_dir, 'model.pkl'))
        joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
        with open(os.path.join(models_dir, 'model_name.txt'), 'w') as f:
            f.write(best_model_name)

        # Generate correlation matrix image
        correlation_plot = None
        try:
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
            correlation_plot = image_base64
        except Exception as e:
            correlation_plot = None

        # Context for template (we pass the best metrics)
        context = {
            'best_model_name': best_model_name,
            'mae': f"{best_metrics['mae']:.2f}",
            'mse': f"{best_metrics['mse']:.2f}",
            'rmse': f"{best_metrics['rmse']:.2f}",
            'r2': f"{best_metrics['r2']:.4f}",
            'comparison_results': comparison_results,
            'correlation_plot': correlation_plot
        }

        return render(request, 'users/training.html', context)

    except Exception as e:
        error_msg = f"Error during model training: {str(e)}"
        print(error_msg)
        return render(request, 'users/training.html', {'error': error_msg})


def predict_view(request):
    prediction = None
    model_name_used = "Unknown"

    try:
        # Check which model was saved as the best
        with open(os.path.join(BASE_DIR, 'models', 'model_name.txt'), 'r') as f:
            model_name_used = f.read().strip()
    except Exception:
        model_name_used = "Model (Name Not Found)"

    if request.method == 'POST':
        # Load saved model and scaler
        model = joblib.load(os.path.join(BASE_DIR, 'models', 'model.pkl'))
        scaler = joblib.load(os.path.join(BASE_DIR, 'models', 'scaler.pkl'))

        # Get input data
        try:
            features = [
                float(request.POST['wind_speed']),
                float(request.POST['wind_dir']),
                float(request.POST['temp']),
                float(request.POST['rotor_speed']),
                float(request.POST['pressure'])
            ]
            features_scaled = scaler.transform([features])
            prediction = model.predict(features_scaled)[0]
        except Exception as e:
            prediction = f"Error: {e}"

    return render(request, 'users/prediction.html', {
        'prediction': prediction, 
        'model_name': model_name_used
    })


def view_dataset(request):
    # Replace this with your real dataset logic
    return render(request, 'users/viewdataset.html')


import pandas as pd
from django.shortcuts import render
import os
from django.conf import settings

def view_dataset(request):
    dataset_path = os.path.join(settings.MEDIA_ROOT, 'wind_power_dataset_50000.csv')  # Ensure file is there
    df = pd.read_csv(dataset_path)
    df = df.head(500)  # Limit to first 500 rows
    table_html = df.to_html(classes='table table-striped table-bordered', index=False, border=0)
    return render(request, 'users/viewdataset.html', {'table': table_html})

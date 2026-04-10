from django.shortcuts import render,redirect
from django.contrib import messages
from users.models import UserRegistrationModel
import os
from django.conf import settings


# Create your views here.
def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("User ID is = ", usrid)
        if usrid == 'admin' and pswd == 'admin':
            total_users = UserRegistrationModel.objects.count()
            best_model = "Not Trained Yet"
            try:
                models_path = os.path.join(settings.BASE_DIR, 'models', 'model_name.txt')
                if os.path.exists(models_path):
                    with open(models_path, 'r') as f:
                        best_model = f.read().strip()
            except Exception:
                pass
            return render(request, 'admins/AdminHome.html', {'total_users': total_users, 'best_model': best_model})

        else:
            messages.success(request, 'Please Check Your Login Details')
    return render(request, 'AdminLogin.html', {})



def RegisterUsersView(request):
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/viewregisterusers.html', context={'data': data})




def ActivaUsers(request):
    if request.method == 'GET':
        user_id = request.GET.get('uid')
        
        if user_id:  # Ensure user_id is not None
            status = 'activated'
            print("Activating user with ID =", user_id)
            UserRegistrationModel.objects.filter(id=user_id).update(status=status)

        # Redirect to the view where users are listed after activation
        return redirect('RegisterUsersView')  # Replace with your actual URL name

def DeleteUsers(request):
    if request.method == 'GET':
        user_id = request.GET.get('uid')
        
        if user_id:  # Ensure user_id is not None
            print("Deleting user with ID =", user_id)
            UserRegistrationModel.objects.filter(id=user_id).delete()

        # Redirect to the view where users are listed after deletion
        return redirect('RegisterUsersView')  # Replace with your actual URL name


def AdminHome(request):
    total_users = UserRegistrationModel.objects.count()
    best_model = "Not Trained Yet"
    try:
        models_path = os.path.join(settings.BASE_DIR, 'models', 'model_name.txt')
        if os.path.exists(models_path):
            with open(models_path, 'r') as f:
                best_model = f.read().strip()
    except Exception:
        pass
    return render(request, 'admins/AdminHome.html', {'total_users': total_users, 'best_model': best_model})
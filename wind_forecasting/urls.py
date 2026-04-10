"""
URL configuration for wind_forecasting project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from wind_forecasting import views as mv
from admins import views as admins
from users import views as usr  # unified import

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Landing & Authentication
    path('', mv.index, name='index'),
    path('index/', mv.index, name='index'),
    path('Adminlogin/', mv.AdminLogin, name='AdminLogin'),
    path('UserLogin/', mv.UserLogin, name='UserLogin'),
    path('UserLoginCheck/', usr.UserLoginCheck, name='UserLoginCheck'),
    path('UserRegisterForm/', usr.UserRegisterActions, name='UserRegisterForm'),

    # Admin Panel
    path('Adminlogin/AdminLogincheck/', admins.AdminLoginCheck, name='AdminLoginCheck'),
    path('AdminHome/', admins.AdminHome, name='AdminHome'),
    path('userDetails/', admins.RegisterUsersView, name='RegisterUsersView'),
    path('ActivUsers/', admins.ActivaUsers, name='activate_users'),
    path('DeleteUsers/', admins.DeleteUsers, name='delete_users'),

    # User Panel
    path('UserHome/', usr.UserHome, name='UserHome'),
    path('viewdataset/', usr.view_dataset, name='viewdataset'),  # Added View Dataset
    path('train/', usr.train_view, name='train'),                # Added Training
    path('predict/', usr.predict_view, name='predict'),          # Added Prediction
    path('logout/', usr.logout_view, name='logout'),             # Logout
]

# Media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

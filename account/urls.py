
# urls.py
from django.urls import path
from account.views import *

urlpatterns = [
    path('', UserLogin, name='login'),
    path('register/',UserRegister,name="register"),
    path('logout/',UseLogout,name="logout"),
    
]


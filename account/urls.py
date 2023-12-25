
# urls.py
from django.urls import path
from account.views import UserLogin

urlpatterns = [
    path('', UserLogin, name='login'),
    
]


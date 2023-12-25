# from django.urls import path
# from .views import *

# urlpatterns = [
#    path('send/',send_message,name='send_message'),
#    path('get/',get_message,name='get_message'),
# ]


# urls.py
from django.urls import path
from account.views import UserLogin

urlpatterns = [
    path('', UserLogin, name='login'),
    
]


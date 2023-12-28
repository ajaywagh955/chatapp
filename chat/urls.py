# urls.py
from django.urls import path
from chat.views import *

urlpatterns = [
    path('',FirstPage,name="index"),
    path('room/<uuid:room_id>/', chat_room, name='chat_room'),    
    path('get_messages/<uuid:room_id>/', get_messages, name='get_messages'),
    path('save_message/<uuid:room_id>/', save_message, name='save_message'),   
    path('edit_message/<int:message_id>/', edit_message, name='edit_message'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('send_request/', send_request, name='send_request'),
    path('accept_request/<int:request_id>/', accept_request, name='accept_request'),
    path('reject_request/<int:request_id>/', reject_request, name='reject_request'),   
    path('fr/friendship_management/', friendship_management, name='friendship_management'),
]



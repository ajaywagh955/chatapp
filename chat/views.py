from django.shortcuts import render, redirect,get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import *
# Create your views here.

# @login_required(login_url="login")
# def FirstPage(request):
#     user_rooms = request.user.rooms.all()
#     return render(request, 'chat/index.html', {'rooms': user_rooms})


@login_required(login_url="login")
def FirstPage(request):
    user_rooms = request.user.rooms.all()

    # Example: Assume you have a field 'icon' in your Room model and 'profile_pic' in your UserProfile model
    room_icons = [room.room_icon.url if room.room_icon else '' for room in user_rooms]
    
    # Assuming UserProfile has a OneToOneField with User
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile_pic = user_profile.profile_picture.url if user_profile.profile_picture else ''

    return render(request, 'chat/index.html', {
        'rooms': user_rooms,
        'room_icons': room_icons,
        'user_profile_pic': user_profile_pic,
    })


@csrf_exempt
@login_required(login_url="login")
def save_message(request, room_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        sender = request.user
        room = Room.objects.get(pk=room_id)

        if content:
            message = Message.objects.create(content=content, sender=sender, room=room)
            data = {
                'content': message.content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'sender': message.sender.username,
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'Invalid content'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


@login_required(login_url="login")
def get_messages(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    messages = Message.objects.filter(room=room).order_by('id')       
    
    
    if request.user not in room.members.all():
        # Redirect to a "not authorized" page or handle it as needed
        return render(request, 'chat/not_authorized.html')
    
    
    message_list = []
    for message in messages:
        message_data = {
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender': message.sender.username
        }
        message_list.append(message_data)

    return JsonResponse({'messages': message_list})


@login_required(login_url="login")
def chat_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    messages = Message.objects.filter(room=room).order_by('id')
    
    if not  request.user in room.members.all():
        return render(request, 'chat/not_authorized.html')
    
    room_name = room.name
    room_icon = room.room_icon.url if room.room_icon else ''   
    return render(request, 'chat/chat.html', {'room': room, 'messages': messages, 'room_id': room_id,'room_name':room_name, 'room_icon': room_icon})







@login_required(login_url="login")
def send_request(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        try:
            to_user = User.objects.get(username=username)
            from_user = request.user

            # Check if the request is valid (not to oneself, not already friends)
            if to_user != from_user and not Friendship.objects.filter(from_user=from_user, to_user=to_user, is_accepted=True).exists():
                # Check if a pending request already exists
                existing_request = Friendship.objects.filter(from_user=from_user, to_user=to_user, is_accepted=False)
                
                # Ensure the user is not sending a request to themselves
                if from_user != to_user:
                    if not existing_request.exists():
                        Friendship.objects.create(from_user=from_user, to_user=to_user)
                        return JsonResponse({'message': 'Friend request sent successfully!'})
                    else:
                        return JsonResponse({'message': 'Friend request already sent.'})
                else:
                    return JsonResponse({'message': 'You cannot send a friend request to yourself.'})
            else:
                return JsonResponse({'message': 'Invalid friend request. You might be friends already or trying to send a request to yourself.'})

        except User.DoesNotExist:
            return JsonResponse({'message': 'User does not exist.'})

    return JsonResponse({'message': 'Invalid request method.'})


@login_required(login_url="login")
def accept_request(request, request_id):
    friendship_request = get_object_or_404(Friendship, id=request_id, to_user=request.user, is_accepted=False)
    
    # Accept the friend request
    friendship_request.is_accepted = True
    friendship_request.save()

    return redirect('friendship_management')

@login_required(login_url="login")
def reject_request(request, request_id):
    friendship_request = get_object_or_404(Friendship, id=request_id, to_user=request.user, is_accepted=False)
    
    # Delete the friend request
    friendship_request.delete()

    return redirect('friendship_management')



# 
@login_required(login_url="login")
def friendship_management(request):
    incoming_requests = Friendship.objects.filter(to_user=request.user, is_accepted=False)
    
    friends = Friendship.objects.filter(
        Q(from_user=request.user, is_accepted=True) | Q(to_user=request.user, is_accepted=True)
    )
    # Extract unique user objects from friends
    friends_users = set()
    for friend in friends:
        friends_users.add(friend.from_user)
        friends_users.add(friend.to_user)

    return render(request, 'chat/friendship/friendship_management.html', {'friends': friends_users,'incoming_requests': incoming_requests},)
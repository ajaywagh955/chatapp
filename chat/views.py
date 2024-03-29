from django.shortcuts import render, redirect,get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Q
from .models import *
from django.views.decorators.http import require_POST
from .models import Message
from django.http import HttpResponseBadRequest
# Create your views here.



@login_required(login_url="login")
def FirstPage(request):
    user_rooms = request.user.rooms.all()

    room_icons = [room.room_icon.url if room.room_icon else '' for room in user_rooms]
    
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
        return render(request, 'chat/not_authorized.html')
    
    message_list = []
    for message in messages:
        message_data = {
            'id':message.id,
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

            if to_user != from_user and not Friendship.objects.filter(from_user=from_user, to_user=to_user, is_accepted=True).exists():

                existing_request = Friendship.objects.filter(from_user=from_user, to_user=to_user, is_accepted=False)
                
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
    
    friendship_request.is_accepted = True
    friendship_request.save()

    return redirect('friendship_management')

@login_required(login_url="login")
def reject_request(request, request_id):
    friendship_request = get_object_or_404(Friendship, id=request_id, to_user=request.user, is_accepted=False)
    
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




@login_required(login_url="login")
@csrf_exempt
@require_POST
def edit_message(request, message_id):
    
    message = Message.objects.get(id=message_id)
    
    new_content = request.POST.get('content')
    
    
    if message.sender == request.user:
        if new_content:
            message.content = new_content
            message.save()
                
            return JsonResponse({'status': 'success', 'message': 'Message updated successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'New message content is empty'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized to edit this message'})
        

@login_required(login_url="login")
@csrf_exempt
@require_POST
def delete_message(request, message_id):
    try:
        message = Message.objects.filter(pk=message_id)
        message.delete()
        print(message)
        print("Message Deleted")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': str(e)})
    
    
    
# User Presend and Is Typing logical Views



@require_POST
@csrf_exempt
@login_required(login_url="login")
def check_user_presence(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    user_last_activity_key = f'user_last_activity_{request.user.id}_room_{room_id}'
    last_activity_time = request.session.get(user_last_activity_key)

    if last_activity_time:
        # Check if the user was active in the last 5 minutes
        is_online = datetime.now() - last_activity_time < timedelta(minutes=5)
    else:
        is_online = False

    return JsonResponse({'is_online': is_online})

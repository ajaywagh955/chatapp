from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    members = models.ManyToManyField(User, related_name='rooms')
    room_icon = models.ImageField(upload_to="room_icon/",blank=True,null=True)
    
    def __str__(self):
        return f" Room ID :- {self.id} -- Room Name :- {self.name} ----- Members :- {self.members} "
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Room, self).save(*args, **kwargs)

class Message(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Sender :- {self.sender} --- Room :- {self.room}"
    
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    mobile_number = models.IntegerField(blank=True)
    friends = models.ManyToManyField(User, related_name='my_friends', blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # Add any additional fields you need for the user profile
    
    
    def __str__(self):
        return f"User Name :- {self.user}"
    
    
    
class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendship_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_to', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user.username} to {self.to_user.username}, Accepted: {self.is_accepted}"
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from chat.models import *
# Create your views here.



def UserLogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        
        user_check = User.objects.filter(username=username).first()
        
        if user_check is None:
            messages.success(request,f"{username} - Not Found")
            return redirect('login')
        
        user = authenticate(username=username,password=password)
        
        if user is None:
            messages.success(request,"Wrong Password")
            return redirect('login')
        
        login(request, user)
        
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        
        else:
            print("Login SuccessFully")
            return redirect('/')
           
    
    return render(request,'account/login.html')
            
            
def UserRegister(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        username = request.POST.get('username')
        password = request.POST.get('password')
        c_password = request.POST.get('c_password')
        profile_picture = request.FILES['image']
        
        if password==c_password:
            if UserProfile.objects.filter(mobile_number=mobile_number).exists():
                messages.success(request,f"{mobile_number} - This Mobile Number Already Exists")
                return redirect("register")
            if User.objects.filter(username=username).exists():
                messages.success(request,f"{username} -- This Username Already Taken")
                return redirect("register")
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(username=username,password=password,first_name=first_name,last_name=last_name,email=email)
                user.save()
                
                user_obj = UserProfile.objects.create(
                    user=user,
                    mobile_number=mobile_number,
                    profile_picture=profile_picture
                )
                
                return redirect("login")
            else:
                messages.success(request,f"{email} - This Email Already Exist")
                return redirect("register")
        else:
            messages.success(request,"Password Not Match")
            return redirect("register")
                
    return render(request,'account/register.html')


def UseLogout(request):
    logout(request)
    return redirect("/")
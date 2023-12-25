from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
# Create your views here.



def UserLogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        
        user_check = User.objects.filter(username=username).first()
        
        if user_check is None:
            messages.success(request,"User Not Found")
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
            
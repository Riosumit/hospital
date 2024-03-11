from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from api.models import UserDetail
from api.serializers import UserDetailSerializer

# Create your views here.

def doctor_signup(request):
    msg=""
    username = request.POST.get('username',"")
    email = request.POST.get('email',"")
    first_name = request.POST.get('first_name',"")
    last_name = request.POST.get('last_name',"")
    password = request.POST.get('password',"")
    confirm_password = request.POST.get('confirm_password',"")
    profile_picture = request.FILES.get('profile_picture',"")
    line = request.POST.get('line',"")
    city = request.POST.get('city',"")
    state = request.POST.get('state',"")
    pincode = request.POST.get('pincode',"")
    user_data = {'username': username,'email': email,'first_name': first_name,'last_name': last_name,'password': password,'confirm_password': confirm_password,'profile_picture': profile_picture,'line': line,'city': city,'state': state,'pincode': pincode,}
    if request.method == 'POST':
        if password != confirm_password:
            msg = 'Password and Confirm Password do not match'
        else:
            try:
                user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
                serializer = UserDetailSerializer(data=user_data, context={'user': user, 'user_type':'doctor'})
                if serializer.is_valid():
                    serializer.save()
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    return redirect('doctor_dashboard')
                else:
                    print(serializer.errors)
            except Exception as e:
                print(str(e))
                msg = 'Username already exists'
    return render(request, 'doctor_signup.html', {'msg':msg, 'user_data':user_data})

def patient_signup(request):
    msg=""
    username = request.POST.get('username',"")
    email = request.POST.get('email',"")
    first_name = request.POST.get('first_name',"")
    last_name = request.POST.get('last_name',"")
    password = request.POST.get('password',"")
    confirm_password = request.POST.get('confirm_password',"")
    profile_picture = request.FILES.get('profile_picture',"")
    line = request.POST.get('line',"")
    city = request.POST.get('city',"")
    state = request.POST.get('state',"")
    pincode = request.POST.get('pincode',"")
    user_data = {'username': username,'email': email,'first_name': first_name,'last_name': last_name,'password': password,'confirm_password': confirm_password,'profile_picture': profile_picture,'line': line,'city': city,'state': state,'pincode': pincode,}
    if request.method == 'POST':
        if password != confirm_password:
            msg = 'Password and Confirm Password do not match'
        else:
            try:
                user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
                serializer = UserDetailSerializer(data=user_data, context={'user': user, 'user_type':'patient'})
                if serializer.is_valid():
                    serializer.save()
                    user = authenticate(username=username, password=password)
                    msg = 'Registered Successfully'
                    login(request, user)
                    return redirect('patient_dashboard')
                else:
                    print(serializer.errors)
            except Exception as e:
                print(str(e))
                msg = 'Username already exists'
    return render(request, 'patient_signup.html', {'msg':msg, 'user_data':user_data})

def user_login(request):
    msg = ""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            try:
                user_detail = UserDetail.objects.get(user=user)
                login(request,user)
                if user_detail.user_type == 'patient':
                    return redirect('patient_dashboard')
                elif user_detail.user_type == 'doctor':
                    return redirect('doctor_dashboard')
            except UserDetail.DoesNotExist:
                msg = "User detail not found"
        else:
            msg = "Invalid Username or Password"
    return render(request, 'login.html', {"msg": msg})


def user_logout(request):
    logout(request)
    return redirect('login')

def patient_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user_detail = UserDetail.objects.get(user=request.user)
    serializer = UserDetailSerializer(user_detail)
    print(serializer.data)
    return render(request, 'patient_dashboard.html', serializer.data)

def doctor_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user_detail = UserDetail.objects.get(user=request.user)
    serializer = UserDetailSerializer(user_detail)
    return render(request, 'doctor_dashboard.html', {"user_detail": serializer.data})

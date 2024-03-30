from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from api.models import UserDetail, Blog
from api.serializers import UserDetailSerializer, BlogSerializer, DetailBlogSerializer
from datetime import timedelta, datetime
from google.auth import jwt
from google.oauth2 import id_token
import requests as google_requests
from django.conf import settings
from googleapiclient.discovery import build
import google.oauth2.credentials
import json
from urllib.parse import urlencode

# Create your views here.

def google_auth_redirect(request):
    redirect_uri = settings.GOOGLE_OAUTH2_CALLBACK_URL
    params = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile https://www.googleapis.com/auth/calendar',
        'prompt': 'consent' 
    }
    auth_url = f'https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}'
    return redirect(auth_url)

def google_auth_callback(request):
    code = request.GET.get('code')
    redirect_uri = settings.GOOGLE_OAUTH2_CALLBACK_URL
    token_endpoint = 'https://oauth2.googleapis.com/token'
    response = google_requests.post(token_endpoint, json={
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    })
    token_response = response.json()
    access_token = token_response.get('access_token')
    refresh_token = token_response.get('refresh_token')
    print(token_response)
    print(access_token, refresh_token)
    if(not access_token):
        return redirect('google_auth_redirect')
    my_token = json.dumps({
        'token': access_token,
        'refresh_token': token_response.get('refresh_token'),
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET
    })
    email = request.session['email']
    user = User.objects.get(email=email)
    user_detail = UserDetail.objects.get(user=user)
    user_detail.google_auth_token = my_token
    user_detail.save()
    login(request, user)
    return redirect('home')

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
                    request.session['user_type'] = 'doctor'
                    request.session['email'] = email
                    return redirect('google_auth_redirect')
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
                    request.session['user_type'] = 'patient'
                    return redirect('home')
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
                    request.session['user_type'] = 'patient'
                    return redirect('home')
                elif user_detail.user_type == 'doctor':
                    request.session['user_type'] = 'doctor'
                    return redirect('home')
            except UserDetail.DoesNotExist:
                msg = "User detail not found"
        else:
            msg = "Invalid Username or Password"
    return render(request, 'login.html', {"msg": msg})


def user_logout(request):
    logout(request)
    return redirect('login')

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    blogs = Blog.objects.filter(draft=False).order_by('-id')
    myblogs = Blog.objects.filter(user=request.user).order_by('-id')
    
    mental = request.POST.get('MentalHealth')
    heart = request.POST.get('HeartDisease')
    covid = request.POST.get('Covid19')
    immunization = request.POST.get('Immunization')
    section = request.POST.get('section')

    filtered_categories = {
        "mental": mental,
        "heart": heart,
        "covid": covid,
        "immunization": immunization
    }

    if request.method == 'POST' and (mental or immunization or heart or covid):
        if not mental:
            blogs = blogs.exclude(category='Mental Health')
            myblogs = myblogs.exclude(category='Mental Health')
        if not heart:
            blogs = blogs.exclude(category='Heart Disease')
            myblogs = myblogs.exclude(category='Heart Disease')
        if not covid:
            blogs = blogs.exclude(category='Covid19')
            myblogs = myblogs.exclude(category='Covid19')
        if not immunization:
            blogs = blogs.exclude(category='Immunization')
            myblogs = myblogs.exclude(category='Immunization')

    serializer = DetailBlogSerializer(blogs, many=True)
    myblogserializer = DetailBlogSerializer(myblogs, many=True)

    if request.session['user_type'] == "patient":
        return render(request, 'patient_home.html',{
        "blogs": serializer.data,
        "filtered_categories": filtered_categories,
        "section": section
    })
    
    return render(request, 'doctor_home.html', {
        "blogs": serializer.data,
        "myblogs": myblogserializer.data,
        "filtered_categories": filtered_categories,
        "section": section
    })

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user_detail = UserDetail.objects.get(user=request.user)
    serializer = UserDetailSerializer(user_detail)
    if request.session['user_type'] == "patient":
        return render(request, 'patient_dashboard.html', serializer.data)
    else:
        return render(request, 'doctor_dashboard.html', serializer.data)

def post_blog(request):
    msg = ""
    if not request.user.is_authenticated:
        return redirect('login')
    elif request.session.get('user_type') != 'doctor':
        return redirect('home')
    title = request.POST.get('title', '')
    image = request.FILES.get('image', None)
    category = request.POST.get('category', '')
    summary = request.POST.get('summary', '')
    content = request.POST.get('content', '')
    draft = request.POST.get('draft', False)
    data = {
        'title': title,
        'image': image,
        'category': category,
        'summary': summary,
        'content': content,
        'draft': draft
    }
    if request.method == 'POST':
        serializer = BlogSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            if serializer.validated_data.get('draft'):
                msg = 'Blog added to Draft successfully'
            else:
                msg = 'Blog posted successfully'
            data = {
                'title': "",
                'category': "",
                'summary': "",
                'content': "",
                'draft': False
            }
        else:
            msg = "Invalid Input"
    return render(request, 'add_blog.html', {'msg': msg, 'data': data})

def appointment(request):
    if not request.user.is_authenticated:
        return redirect('login')
    elif request.session.get('user_type') != 'patient':
        return redirect('home')
    doctors = UserDetail.objects.filter(user_type="doctor")
    serializer = UserDetailSerializer(doctors, many=True)
    return render(request, 'appointment.html', {'doctors': doctors})

def book_appointment(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    elif request.session.get('user_type') != 'patient':
        return redirect('home')
    
    msg = ''
    if request.method == "POST":
        speciality = request.POST.get('required_speciality', '')
        date_str = request.POST.get('date', '')
        time_str = request.POST.get('time', '') 
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()
        except Exception as e:
            print(e)
            msg = 'Invalid date or time format'
            return render(request, 'book_appointment.html', {'msg': msg})
        
        doctor = User.objects.get(id=id)
        doctor_detail = UserDetail.objects.get(user=doctor)
        patient = request.user
        
        start_datetime = datetime.combine(date, time)
        end_datetime = start_datetime + timedelta(minutes=45)

        if start_datetime < datetime.now():
            msg = "Appointment date cannot be in the past."
        else:
            credentials_data = json.loads(doctor_detail.google_auth_token)
            credentials = google.oauth2.credentials.Credentials(
                token=credentials_data['token'],
                refresh_token=credentials_data['refresh_token'],
                token_uri=credentials_data['token_uri'],
                client_id=credentials_data['client_id'],
                client_secret=credentials_data['client_secret']
            )

            # Refresh the access token if necessary
            if credentials.expired:
                credentials.refresh(google_requests.Request())
            service = build('calendar', 'v3', credentials=credentials)
            event = {
                'summary': f'Appointment with {doctor.get_full_name()}',
                'description': f'Appointment with {doctor.get_full_name()} for {speciality}',
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'UTC+5:30',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'UTC+5:30',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
                'location': 'Medical Center',
                'attendees': [
                    {'email': doctor.email},
                    {'email': patient.email}
                ],
                'visibility': 'default'
            }

            event = service.events().insert(calendarId='primary', body=event).execute()
            print('Event created:', event.get('htmlLink'))
            return render(request, 'confirmation.html', {'profile_picture': doctor_detail.profile_picture, 'name': doctor.get_full_name(), 'date': date, 'start_time': start_datetime.time(), 'end_time': end_datetime.time()})
    
    return render(request, 'book_appointment.html', {'msg': msg})
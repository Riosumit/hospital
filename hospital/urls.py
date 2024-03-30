"""
URL configuration for hospital project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from .views import doctor_signup, patient_signup, user_login, user_logout, home, dashboard, post_blog, appointment, book_appointment, google_auth_callback, google_auth_redirect
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('doctor/signup', doctor_signup, name='doctor_signup'),
    path('patient/signup', patient_signup, name='patient_signup'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('auth/google/', google_auth_redirect, name='google_auth_redirect'),
    path('auth/google/callback/', google_auth_callback, name='google_auth_callback'),
    path('home', home, name='home'),
    path('post-blog', post_blog, name='post_blog'),
    path('dashboard', dashboard, name='dashboard'),
    path('appointment', appointment, name='appointment'),
    path('appointment/book_appointment/<int:id>', book_appointment, name='book_appointment'),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT})
]

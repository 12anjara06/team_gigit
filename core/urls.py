from django.urls import path
from . import views

from django.views.generic import RedirectView

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', RedirectView.as_view(url='/', permanent=True)),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('api/face-login/', views.face_login_api, name='face_login_api'),
    path('api/save-face-encoding/', views.save_face_encoding, name='save_face_encoding'),
    path('profile/', views.profile_view, name='profile'),
]

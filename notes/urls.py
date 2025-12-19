from django.urls import path
from . import views

urlpatterns = [
    path('', views.note_list, name='note_list'),
    path('d/<int:note_id>/', views.note_list, name='note_list_detail'),
    path('create/', views.note_create, name='note_create'),
    path('<int:note_id>/', views.note_detail, name='note_detail'),
    path('<int:note_id>/delete/', views.note_delete, name='note_delete'),
    
    # Community
    path('community/', views.community_list, name='community_list'),
    path('community/create/', views.community_post_create, name='community_post_create'),
    path('community/<int:question_id>/', views.community_post_detail, name='community_post_detail'),
    path('community/<int:question_id>/answer/', views.community_answer_create, name='community_answer_create'),
]

# chatbot_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from chatbot_app import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('add_articles/<int:chat_session_id>/<int:num_articles>/', views.add_articles, name='add_articles'),
    path('chatbot/<int:chat_session_id>/', views.chatbot, name='chatbot'),
]
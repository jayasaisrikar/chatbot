# chatbot_app/models.py
from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Article(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    url = models.URLField()
    content = models.TextField()

class ChatMessage(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
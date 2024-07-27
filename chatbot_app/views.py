# chatbot_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, ChatSessionForm, ArticleForm, ChatMessageForm
from .models import ChatSession, Article, ChatMessage
from .utils import fetch_and_process_article, create_vector_store, build_query_agent

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def home(request):
    if request.method == 'POST':
        form = ChatSessionForm(request.POST)
        if form.is_valid():
            product_name = form.cleaned_data['product_name']
            num_articles = form.cleaned_data['num_articles']
            chat_session = ChatSession.objects.create(user=request.user, product_name=product_name)
            return redirect('add_articles', chat_session_id=chat_session.id, num_articles=num_articles)
    else:
        form = ChatSessionForm()
    return render(request, 'home.html', {'form': form})

@login_required
def add_articles(request, chat_session_id, num_articles):
    chat_session = ChatSession.objects.get(id=chat_session_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            content = fetch_and_process_article(url)
            Article.objects.create(chat_session=chat_session, url=url, content=content)
            num_articles -= 1
            if num_articles > 0:
                return redirect('add_articles', chat_session_id=chat_session.id, num_articles=num_articles)
            else:
                return redirect('chatbot', chat_session_id=chat_session.id)
    else:
        form = ArticleForm()
    return render(request, 'add_articles.html', {'form': form, 'num_articles': num_articles})

@login_required
def chatbot(request, chat_session_id):
    chat_session = ChatSession.objects.get(id=chat_session_id)
    articles = Article.objects.filter(chat_session=chat_session)
    vector_store = create_vector_store([article.content for article in articles])
    query_agent = build_query_agent(vector_store)

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            bot_response = query_agent(user_message)
            ChatMessage.objects.create(chat_session=chat_session, user_message=user_message, bot_response=bot_response)
            return redirect('chatbot', chat_session_id=chat_session.id)
    else:
        form = ChatMessageForm()

    chat_messages = ChatMessage.objects.filter(chat_session=chat_session).order_by('timestamp')
    return render(request, 'chatbot.html', {
        'form': form,
        'chat_session': chat_session,
        'chat_messages': chat_messages
    })
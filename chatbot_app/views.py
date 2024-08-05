# chatbot_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, ChatSessionForm, ArticleForm, ChatMessageForm
from .models import ChatSession, Article, ChatMessage
from .utils import fetch_and_process_article, create_vector_store, build_query_agent
import re

def format_table(table_text):
    lines = table_text.strip().split('\n')
    if len(lines) < 2:
        return table_text

    html = '<table class="w-full border-collapse">\n<thead>\n<tr>'
    headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
    for header in headers:
        html += f'<th class="border border-gray-600 bg-gray-700 p-2 text-left">{header}</th>'
    html += '</tr>\n</thead>\n<tbody>'

    for line in lines[2:]:
        if not line.strip():
            continue
        html += '<tr>'
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        for cell in cells:
            html += f'<td class="border border-gray-600 bg-gray-800 p-2">{cell}</td>'
        html += '</tr>\n'

    html += '</tbody></table>'
    return html

def format_bot_response(response):
    # Find all table-like structures and replace them with HTML tables
    def replace_table(match):
        return format_table(match.group(0))
    
    formatted_response = re.sub(r'\|[\s\S]+?\|[\s\S]+?(?=\n\n|\Z)', replace_table, response)
    
    # Convert markdown-style bold to HTML bold
    formatted_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_response)
    
    # Convert markdown-style italic to HTML italic
    formatted_response = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted_response)
    
    return formatted_response

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
            
            # Format the bot's response
            formatted_bot_response = format_bot_response(bot_response)
            
            ChatMessage.objects.create(chat_session=chat_session, user_message=user_message, bot_response=formatted_bot_response)
            return redirect('chatbot', chat_session_id=chat_session.id)
    else:
        form = ChatMessageForm()

    chat_messages = ChatMessage.objects.filter(chat_session=chat_session).order_by('timestamp')
    return render(request, 'chatbot.html', {
        'form': form,
        'chat_session': chat_session,
        'chat_messages': chat_messages
    })
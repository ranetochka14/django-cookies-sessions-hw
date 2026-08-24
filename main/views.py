from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if request.POST.get('remember_me'):
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)
                
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect('articles_list')
    else:
        form = AuthenticationForm()
        
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect('login')


SAMPLE_ARTICLES = [
    {'id': 1, 'title': 'Архитектура и чистота кода', 'content': 'Обзор паттернов проектирования...'},
    {'id': 2, 'title': 'Работа с сессиями и Cookie в Django', 'content': 'Подробный гайд по stateful веб-приложениям...'},
    {'id': 3, 'title': 'Безопасность и криптография токенов', 'content': 'Как работает TimestampSigner под капотом...'},
]

def articles_list(request):
    return render(request, 'main/articles.html', {'articles': SAMPLE_ARTICLES})


def toggle_favorite(request, article_id):
    favorites = request.session.get('favorites', [])
    
    if article_id in favorites:
        favorites.remove(article_id)
        messages.warning(request, f"Статья #{article_id} удалена из избранного.")
    else:
        favorites.append(article_id)
        messages.success(request, f"Статья #{article_id} добавлена в избранное!")
        
    request.session['favorites'] = favorites
    request.session.modified = True
    
    return redirect(request.META.get('HTTP_REFERER', 'articles_list'))


def favorites_view(request):
    fav_ids = request.session.get('favorites', [])
    fav_articles = [a for a in SAMPLE_ARTICLES if a['id'] in fav_ids]
    return render(request, 'main/favorites.html', {'articles': fav_articles})


def clear_favorites(request):
    if 'favorites' in request.session:
        del request.session['favorites']
        request.session.modified = True
    messages.info(request, "Список избранного полностью очищен.")
    return redirect('favorites')


def user_settings_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        response = redirect('user_settings')
        
        if action == 'save':
            lang = request.POST.get('lang', 'ru')
            items_per_page = request.POST.get('items_per_page', '10')
            view_mode = request.POST.get('view_mode', 'grid')
            
            # Сохраняем в Cookie на 30 дней
            max_age = 30 * 24 * 60 * 60
            response.set_cookie('lang', lang, max_age=max_age)
            response.set_cookie('items_per_page', items_per_page, max_age=max_age)
            response.set_cookie('view_mode', view_mode, max_age=max_age)
            messages.success(request, "Настройки успешно сохранены в Cookie.")
            
        elif action == 'reset':
            response.delete_cookie('lang')
            response.delete_cookie('items_per_page')
            response.delete_cookie('view_mode')
            messages.info(request, "Настройки сброшены к значениям по умолчанию.")
            
        return response

    current_settings = {
        'lang': request.COOKIES.get('lang', 'ru'),
        'items_per_page': request.COOKIES.get('items_per_page', '10'),
        'view_mode': request.COOKIES.get('view_mode', 'grid'),
    }
    return render(request, 'main/settings.html', {'settings': current_settings})



def download_page(request):
    signer = TimestampSigner()
    payload = {
        'file': 'report.pdf',
        'user': request.user.id if request.user.is_authenticated else 25
    }
    # Подписываем данные
    token = signer.sign_object(payload)
    return render(request, 'main/download.html', {'token': token})


def download_file(request):
    token = request.GET.get('token')
    if not token:
        messages.error(request, "Токен для скачивания отсутствует.")
        return redirect('download_page')
        
    signer = TimestampSigner()
    try:
        # max_age = 300 секунд (5 минут)
        data = signer.unsign_object(token, max_age=300)
        messages.success(request, f"Файл {data['file']} успешно подтвержден и скачан!")
        
        response = HttpResponse(
            f"Тестовый контент файла: {data['file']} для user_id={data['user']}",
            content_type="text/plain; charset=utf-8"
        )
        response['Content-Disposition'] = f'attachment; filename="{data["file"]}"'
        return response
        
    except SignatureExpired:
        messages.error(request, "Ошибка: Срок действия ссылки (5 минут) истек!")
        return redirect('download_page')
    except BadSignature:
        messages.error(request, "Ошибка: Недействительная или измененная подпись ссылки!")
        return redirect('download_page')
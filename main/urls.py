from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.articles_list, name='articles_list'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('favorites/toggle/<int:article_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/clear/', views.clear_favorites, name='clear_favorites'),
    path('settings/', views.user_settings_view, name='user_settings'),
    path('download-page/', views.download_page, name='download_page'),
    path('download-file/', views.download_file, name='download_file'),
]
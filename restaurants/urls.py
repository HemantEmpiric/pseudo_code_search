from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('search/', views.search_view, name='search'),
    path('details/', views.details_view, name='details'),
    path('clear-cache/', views.clear_cache, name='clear_cache'),
]

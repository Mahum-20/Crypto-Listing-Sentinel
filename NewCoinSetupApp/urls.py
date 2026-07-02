from django.urls import path
from NewCoinSetupApp import views

urlpatterns = [
    path('', views.index, name='index'),    
    path('newCoin/checklist/', views.new_coin_guide, name='new_coin_checklist'),
    path('newCoin/analyzer/', views.new_coin_analyzer, name='new_coin_analyzer'),
    path('newCoin/patterns/', views.new_coin_patterns, name='new_coin_patterns'),
    path('newCoin/analysis/', views.new_coin_analysis, name='new_coin_analysis'),
    path('newCoin/strategy/', views.new_coin_strategy, name='new_coin_strategy'),
    path('correlation-visualizer/', views.correlation_visualizer, name='correlation_visualizer'),

]

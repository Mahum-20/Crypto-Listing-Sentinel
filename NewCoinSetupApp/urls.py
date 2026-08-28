from django.urls import path
from django.contrib.auth import views as auth_views
from NewCoinSetupApp import views

urlpatterns = [
    # Public & Intelligence Tools
    path('', views.index, name='index'),    
    path('newCoin/checklist/', views.new_coin_guide, name='new_coin_checklist'),
    path('newCoin/analyzer/', views.new_coin_analyzer, name='new_coin_analyzer'),
    path('newCoin/patterns/', views.new_coin_patterns, name='new_coin_patterns'),
    path('newCoin/analysis/', views.new_coin_analysis, name='new_coin_analysis'),
    path('newCoin/strategy/', views.new_coin_strategy, name='new_coin_strategy'),
    path('correlation-visualizer/', views.correlation_visualizer, name='correlation_visualizer'),

    # Authentication & User Profile
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Password Reset Flow
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Multi-User Trade Journal & Dashboard
    path('journal/', views.journal_dashboard, name='journal_dashboard'),
    path('journal/trades/', views.trade_list, name='trade_list'),
    path('journal/trades/add/', views.trade_create, name='trade_create'),
    path('journal/trades/<int:trade_id>/', views.trade_detail, name='trade_detail'),
    path('journal/trades/<int:trade_id>/edit/', views.trade_edit, name='trade_edit'),
    path('journal/trades/<int:trade_id>/delete/', views.trade_delete, name='trade_delete'),

    # Psychology Audit, Pattern Edge Matrix, Analytics
    path('journal/fomo-shield/', views.fomo_shield, name='fomo_shield'),
    path('journal/pattern-edge/', views.pattern_edge_matrix, name='pattern_edge_matrix'),
    path('journal/analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('journal/generate-demo/', views.generate_demo_trades, name='generate_demo_trades'),
]

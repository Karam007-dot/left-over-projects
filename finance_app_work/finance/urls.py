from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='finance/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('accounts/', views.accounts_view, name='accounts'),
    path('budgets/', views.budgets_view, name='budgets'),
    path('goals/', views.goals_view, name='goals'),
    path('net-worth/', views.net_worth_view, name='net_worth'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
    path('get-link-token/', views.get_link_token, name='get_link_token'),
    path('exchange-token/', views.exchange_token, name='exchange_token'),
    path('sync/', views.sync_transactions, name='sync_transactions'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('add-goal/', views.add_goal, name='add_goal'),
    path('add-budget/', views.add_budget, name='add_budget'),
    path('delete-account/<int:pk>/', views.delete_account, name='delete_account'),
]

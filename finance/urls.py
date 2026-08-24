from django.urls import path
from finance import views

app_name = 'finance'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Income
    path('income/', views.income_list_view, name='income_list'),
    path('income/add/', views.add_income_view, name='add_income'),
    path('income/edit/<str:income_id>/', views.edit_income_view, name='edit_income'),
    path('income/delete/<str:income_id>/', views.delete_income_view, name='delete_income'),
    
    # Expenses
    path('expenses/', views.expense_list_view, name='expense_list'),
    path('expenses/add/', views.add_expense_view, name='add_expense'),
    path('expenses/edit/<str:expense_id>/', views.edit_expense_view, name='edit_expense'),
    path('expenses/delete/<str:expense_id>/', views.delete_expense_view, name='delete_expense'),
    
    # Budget
    path('budget/', views.budget_view, name='budget'),
    path('budget/delete/<str:budget_id>/', views.delete_budget_view, name='delete_budget'),
    
    # Savings Goals
    path('savings-goals/', views.savings_goals_view, name='savings_goals'),
    path('savings-goals/edit/<str:goal_id>/', views.edit_savings_goal_view, name='edit_savings_goal'),
    path('savings-goals/delete/<str:goal_id>/', views.delete_savings_goal_view, name='delete_savings_goal'),
    
    # Analytics & Reports
    path('analytics/', views.analytics_view, name='analytics'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/download/<str:file_type>/', views.download_report_view, name='download_report'),
]

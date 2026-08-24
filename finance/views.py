import json
from functools import wraps
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404

from finance.forms import (
    RegistrationForm, LoginForm, IncomeForm, ExpenseForm,
    BudgetForm, SavingsGoalForm
)
from finance.services.finance_service import FinanceService
from finance.services.budget_service import BudgetService
from finance.services.analytics_service import AnalyticsService
from finance.services.report_service import ReportService

def login_required_custom(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, "Please log in to access this page.")
            return redirect('finance:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ------------------ AUTH VIEWS ------------------

def home_view(request):
    if request.session.get('user_id'):
        return redirect('finance:dashboard')
    return render(request, 'finance/home.html')

def register_view(request):
    if request.session.get('user_id'):
        return redirect('finance:dashboard')
        
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user_id = FinanceService.register_user(name, email, password)
                messages.success(request, "Account created successfully! Please log in.")
                return redirect('finance:login')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Database Connection Error: Ensure MONGO_URI is configured on Render. ({e})")
    else:
        form = RegistrationForm()
        
    return render(request, 'finance/register.html', {'form': form})

def login_view(request):
    if request.session.get('user_id'):
        return redirect('finance:dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = FinanceService.authenticate_user(email, password)
                if user:
                    request.session['user_id'] = user['_id']
                    request.session['user_name'] = user['name']
                    request.session['user_email'] = user['email']
                    messages.success(request, f"Welcome back, {user['name']}!")
                    return redirect('finance:dashboard')
                else:
                    messages.error(request, "Invalid email address or password. Note: Create a new account via Register if you haven't registered on the online server yet.")
            except Exception as e:
                messages.error(request, f"Database Connection Error: Could not connect to MongoDB Atlas. Ensure MONGO_URI is set in Render environment. ({e})")
    else:
        form = LoginForm()
        
    return render(request, 'finance/login.html', {'form': form})

def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('finance:login')

# ------------------ DASHBOARD VIEW ------------------

@login_required_custom
def dashboard_view(request):
    user_id = request.session['user_id']
    
    try:
        summary = AnalyticsService.get_dashboard_summary(user_id)
        now = datetime.now()
        budget_info = BudgetService.get_budget_analysis(user_id, now.month, now.year)
        analytics = AnalyticsService.get_spending_analytics(user_id)
        
        context = {
            'summary': summary,
            'budget_info': budget_info,
            'analytics': analytics,
            'category_chart_json': json.dumps(analytics['category_chart']),
            'monthly_chart_json': json.dumps(analytics['monthly_chart'])
        }
        return render(request, 'finance/dashboard.html', context)
    except Exception as e:
        messages.error(request, f"Database Error: {e}")
        return render(request, 'finance/dashboard.html', {
            'summary': {'total_income': 0, 'total_expenses': 0, 'current_balance': 0, 'total_savings': 0, 'recent_transactions': []},
            'budget_info': {'exceeded_count': 0},
            'analytics': {'category_chart': {'labels': [], 'data': []}, 'monthly_chart': {'labels': [], 'income_data': [], 'expense_data': []}},
            'category_chart_json': json.dumps({'labels': [], 'data': []}),
            'monthly_chart_json': json.dumps({'labels': [], 'income_data': [], 'expense_data': []})
        })

# ------------------ INCOME VIEWS ------------------

@login_required_custom
def income_list_view(request):
    user_id = request.session['user_id']
    income_list = FinanceService.get_income_by_user(user_id)
    return render(request, 'finance/income.html', {'income_list': income_list})

@login_required_custom
def add_income_view(request):
    user_id = request.session['user_id']
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            source = form.cleaned_data['source']
            amount = form.cleaned_data['amount']
            date_str = form.cleaned_data['date'].strftime('%Y-%m-%d')
            description = form.cleaned_data['description']
            try:
                FinanceService.add_income(user_id, source, amount, date_str, description)
                messages.success(request, "Income recorded successfully!")
                return redirect('finance:income_list')
            except Exception as e:
                messages.error(request, f"Error saving income: {e}")
    else:
        form = IncomeForm(initial={'date': datetime.now().strftime('%Y-%m-%d')})
        
    return render(request, 'finance/add_expense.html', {'form': form, 'title': 'Add Income', 'button_text': 'Save Income', 'back_url': 'finance:income_list'})

@login_required_custom
def edit_income_view(request, income_id):
    user_id = request.session['user_id']
    income_doc = FinanceService.get_income_by_id(user_id, income_id)
    if not income_doc:
        messages.error(request, "Income record not found.")
        return redirect('finance:income_list')
        
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            source = form.cleaned_data['source']
            amount = form.cleaned_data['amount']
            date_str = form.cleaned_data['date'].strftime('%Y-%m-%d')
            description = form.cleaned_data['description']
            try:
                FinanceService.update_income(user_id, income_id, source, amount, date_str, description)
                messages.success(request, "Income updated successfully!")
                return redirect('finance:income_list')
            except Exception as e:
                messages.error(request, f"Error updating income: {e}")
    else:
        dt = income_doc['date']
        date_val = dt.strftime('%Y-%m-%d') if isinstance(dt, datetime) else str(dt)[:10]
        form = IncomeForm(initial={
            'source': income_doc.get('source'),
            'amount': income_doc.get('amount'),
            'date': date_val,
            'description': income_doc.get('description')
        })
        
    return render(request, 'finance/add_expense.html', {'form': form, 'title': 'Edit Income', 'button_text': 'Update Income', 'back_url': 'finance:income_list'})

@login_required_custom
def delete_income_view(request, income_id):
    user_id = request.session['user_id']
    if request.method == 'POST' or request.method == 'GET':
        FinanceService.delete_income(user_id, income_id)
        messages.success(request, "Income record deleted.")
    return redirect('finance:income_list')

# ------------------ EXPENSE VIEWS ------------------

@login_required_custom
def expense_list_view(request):
    user_id = request.session['user_id']
    expenses = FinanceService.get_expenses_by_user(user_id)
    return render(request, 'finance/expenses.html', {'expenses': expenses})

@login_required_custom
def add_expense_view(request):
    user_id = request.session['user_id']
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            amount = form.cleaned_data['amount']
            date_str = form.cleaned_data['date'].strftime('%Y-%m-%d')
            description = form.cleaned_data['description']
            try:
                FinanceService.add_expense(user_id, category, amount, date_str, description)
                messages.success(request, "Expense recorded successfully!")
                return redirect('finance:expense_list')
            except Exception as e:
                messages.error(request, f"Error saving expense: {e}")
    else:
        form = ExpenseForm(initial={'date': datetime.now().strftime('%Y-%m-%d')})
        
    return render(request, 'finance/add_expense.html', {'form': form, 'title': 'Add Expense', 'button_text': 'Save Expense', 'back_url': 'finance:expense_list'})

@login_required_custom
def edit_expense_view(request, expense_id):
    user_id = request.session['user_id']
    expense_doc = FinanceService.get_expense_by_id(user_id, expense_id)
    if not expense_doc:
        messages.error(request, "Expense record not found.")
        return redirect('finance:expense_list')
        
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            amount = form.cleaned_data['amount']
            date_str = form.cleaned_data['date'].strftime('%Y-%m-%d')
            description = form.cleaned_data['description']
            try:
                FinanceService.update_expense(user_id, expense_id, category, amount, date_str, description)
                messages.success(request, "Expense record updated successfully!")
                return redirect('finance:expense_list')
            except Exception as e:
                messages.error(request, f"Error updating expense: {e}")
    else:
        dt = expense_doc['date']
        date_val = dt.strftime('%Y-%m-%d') if isinstance(dt, datetime) else str(dt)[:10]
        form = ExpenseForm(initial={
            'category': expense_doc.get('category'),
            'amount': expense_doc.get('amount'),
            'date': date_val,
            'description': expense_doc.get('description')
        })
        
    return render(request, 'finance/add_expense.html', {'form': form, 'title': 'Edit Expense', 'button_text': 'Update Expense', 'back_url': 'finance:expense_list'})

@login_required_custom
def delete_expense_view(request, expense_id):
    user_id = request.session['user_id']
    if request.method == 'POST' or request.method == 'GET':
        FinanceService.delete_expense(user_id, expense_id)
        messages.success(request, "Expense record deleted.")
    return redirect('finance:expense_list')

# ------------------ BUDGET VIEWS ------------------

@login_required_custom
def budget_view(request):
    user_id = request.session['user_id']
    now = datetime.now()
    month = request.GET.get('month', now.month)
    year = request.GET.get('year', now.year)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            b_month = form.cleaned_data['month']
            b_year = form.cleaned_data['year']
            category = form.cleaned_data['category']
            limit_amount = form.cleaned_data['limit_amount']
            try:
                BudgetService.create_or_update_budget(user_id, b_month, b_year, category, limit_amount)
                messages.success(request, f"Budget limit set for {category}!")
                return redirect(f"/budget/?month={b_month}&year={b_year}")
            except Exception as e:
                messages.error(request, f"Error setting budget: {e}")
    else:
        form = BudgetForm(initial={'month': int(month), 'year': int(year)})
        
    analysis = BudgetService.get_budget_analysis(user_id, month, year)
    return render(request, 'finance/budget.html', {'form': form, 'analysis': analysis})

@login_required_custom
def delete_budget_view(request, budget_id):
    user_id = request.session['user_id']
    BudgetService.delete_budget(user_id, budget_id)
    messages.success(request, "Budget deleted.")
    return redirect('finance:budget')

# ------------------ SAVINGS GOALS VIEWS ------------------

@login_required_custom
def savings_goals_view(request):
    user_id = request.session['user_id']
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal_name = form.cleaned_data['goal_name']
            target_amount = form.cleaned_data['target_amount']
            saved_amount = form.cleaned_data['saved_amount']
            target_date_str = form.cleaned_data['target_date'].strftime('%Y-%m-%d') if form.cleaned_data['target_date'] else ""
            try:
                FinanceService.add_savings_goal(user_id, goal_name, target_amount, saved_amount, target_date_str)
                messages.success(request, "Savings goal added successfully!")
                return redirect('finance:savings_goals')
            except Exception as e:
                messages.error(request, f"Error saving goal: {e}")
    else:
        form = SavingsGoalForm()
        
    goals = FinanceService.get_savings_goals_by_user(user_id)
    return render(request, 'finance/savings_goals.html', {'form': form, 'goals': goals})

@login_required_custom
def edit_savings_goal_view(request, goal_id):
    user_id = request.session['user_id']
    goal = FinanceService.get_savings_goal_by_id(user_id, goal_id)
    if not goal:
        messages.error(request, "Savings goal not found.")
        return redirect('finance:savings_goals')
        
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal_name = form.cleaned_data['goal_name']
            target_amount = form.cleaned_data['target_amount']
            saved_amount = form.cleaned_data['saved_amount']
            target_date_str = form.cleaned_data['target_date'].strftime('%Y-%m-%d') if form.cleaned_data['target_date'] else ""
            try:
                FinanceService.update_savings_goal(user_id, goal_id, goal_name, target_amount, saved_amount, target_date_str)
                messages.success(request, "Savings goal updated successfully!")
                return redirect('finance:savings_goals')
            except Exception as e:
                messages.error(request, f"Error updating savings goal: {e}")
    else:
        td = goal.get('target_date')
        td_val = td.strftime('%Y-%m-%d') if isinstance(td, datetime) else (str(td)[:10] if td else '')
        form = SavingsGoalForm(initial={
            'goal_name': goal.get('goal_name'),
            'target_amount': goal.get('target_amount'),
            'saved_amount': goal.get('saved_amount'),
            'target_date': td_val
        })
        
    return render(request, 'finance/add_expense.html', {'form': form, 'title': 'Edit Savings Goal', 'button_text': 'Update Goal', 'back_url': 'finance:savings_goals'})

@login_required_custom
def delete_savings_goal_view(request, goal_id):
    user_id = request.session['user_id']
    FinanceService.delete_savings_goal(user_id, goal_id)
    messages.success(request, "Savings goal deleted.")
    return redirect('finance:savings_goals')

# ------------------ ANALYTICS & REPORTS ------------------

@login_required_custom
def analytics_view(request):
    user_id = request.session['user_id']
    analytics = AnalyticsService.get_spending_analytics(user_id)
    context = {
        'analytics': analytics,
        'category_chart_json': json.dumps(analytics['category_chart']),
        'monthly_chart_json': json.dumps(analytics['monthly_chart']),
        'savings_trend_json': json.dumps(analytics['savings_trend_chart'])
    }
    return render(request, 'finance/analytics.html', context)

@login_required_custom
def reports_view(request):
    user_id = request.session['user_id']
    now = datetime.now()
    month = request.GET.get('month', now.month)
    year = request.GET.get('year', now.year)
    
    report_data = ReportService.get_monthly_report_data(user_id, month, year)
    
    request.session['report_month'] = int(month)
    request.session['report_year'] = int(year)
    
    return render(request, 'finance/reports.html', {
        'report': report_data,
        'current_month': int(month),
        'current_year': int(year)
    })

@login_required_custom
def download_report_view(request, file_type):
    user_id = request.session['user_id']
    now = datetime.now()
    month = request.session.get('report_month', now.month)
    year = request.session.get('report_year', now.year)

    report_data = ReportService.get_monthly_report_data(user_id, month, year)

    if file_type == 'csv':
        filepath, filename = ReportService.generate_csv_report(report_data)
        response = FileResponse(open(filepath, 'rb'), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    elif file_type == 'pdf':
        filepath, filename = ReportService.generate_pdf_report(report_data)
        response = FileResponse(open(filepath, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        raise Http404("Invalid report format requested.")

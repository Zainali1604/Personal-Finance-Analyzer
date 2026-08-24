from django import forms
from datetime import datetime

INCOME_SOURCES = [
    ('Salary', 'Salary'),
    ('Freelancing', 'Freelancing'),
    ('Business', 'Business'),
    ('Investment', 'Investment'),
    ('Other', 'Other')
]

EXPENSE_CATEGORIES = [
    ('Food', 'Food'),
    ('Travel', 'Travel'),
    ('Shopping', 'Shopping'),
    ('Bills', 'Bills'),
    ('Education', 'Education'),
    ('Entertainment', 'Entertainment'),
    ('Health', 'Health'),
    ('Rent', 'Rent'),
    ('Other', 'Other')
]

MONTH_CHOICES = [
    (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
    (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
    (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
]

class RegistrationForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password (min 6 chars)'}),
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class IncomeForm(forms.Form):
    source = forms.ChoiceField(
        choices=INCOME_SOURCES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    amount = forms.FloatField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'})
    )

class ExpenseForm(forms.Form):
    category = forms.ChoiceField(
        choices=EXPENSE_CATEGORIES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    amount = forms.FloatField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'})
    )

class BudgetForm(forms.Form):
    month = forms.TypedChoiceField(
        choices=MONTH_CHOICES,
        coerce=int,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    year = forms.IntegerField(
        min_value=2000,
        max_value=2100,
        initial=datetime.now().year,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    category = forms.ChoiceField(
        choices=EXPENSE_CATEGORIES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    limit_amount = forms.FloatField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    )

class SavingsGoalForm(forms.Form):
    goal_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Emergency Fund, New Laptop'})
    )
    target_amount = forms.FloatField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    )
    saved_amount = forms.FloatField(
        min_value=0.0,
        initial=0.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    )
    target_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

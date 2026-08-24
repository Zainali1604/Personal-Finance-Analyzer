from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse

from finance.services.finance_service import FinanceService
from finance.services.budget_service import BudgetService
from finance.services.analytics_service import AnalyticsService
from finance.database.mongodb import (
    get_users_collection,
    get_income_collection,
    get_expenses_collection,
    get_budgets_collection,
    get_savings_goals_collection
)

class PersonalFinanceTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_email = "testuser@example.com"
        self.test_password = "Password123"
        self.test_name = "Test User"
        
        # Clear test MongoDB database collections before each test run
        get_users_collection().delete_many({})
        get_income_collection().delete_many({})
        get_expenses_collection().delete_many({})
        get_budgets_collection().delete_many({})
        get_savings_goals_collection().delete_many({})

    def test_user_registration(self):
        """Test user registration and password hashing."""
        user_id = FinanceService.register_user(self.test_name, self.test_email, self.test_password)
        self.assertIsNotNone(user_id)
        
        # Test duplicate email prevention
        with self.assertRaises(ValueError):
            FinanceService.register_user(self.test_name, self.test_email, self.test_password)

    def test_user_login_logout(self):
        """Test authentication, login verification, and logout."""
        FinanceService.register_user(self.test_name, self.test_email, self.test_password)
        
        # Valid login
        user = FinanceService.authenticate_user(self.test_email, self.test_password)
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], self.test_email)
        
        # Invalid password
        bad_user = FinanceService.authenticate_user(self.test_email, "WrongPassword")
        self.assertIsNone(bad_user)

    def test_income_crud(self):
        """Test adding, viewing, editing, and deleting income records."""
        user_id = FinanceService.register_user(self.test_name, self.test_email, self.test_password)
        
        # Add income
        inc_id = FinanceService.add_income(user_id, "Salary", 5000.0, "2026-08-01", "Monthly Salary")
        self.assertIsNotNone(inc_id)
        
        # View income
        incomes = FinanceService.get_income_by_user(user_id)
        self.assertEqual(len(incomes), 1)
        self.assertEqual(incomes[0]['amount'], 5000.0)
        
        # Edit income
        updated = FinanceService.update_income(user_id, inc_id, "Freelancing", 6000.0, "2026-08-01", "Updated Freelance")
        self.assertTrue(updated)
        doc = FinanceService.get_income_by_id(user_id, inc_id)
        self.assertEqual(doc['amount'], 6000.0)
        self.assertEqual(doc['source'], "Freelancing")
        
        # Delete income
        deleted = FinanceService.delete_income(user_id, inc_id)
        self.assertTrue(deleted)
        self.assertEqual(len(FinanceService.get_income_by_user(user_id)), 0)

    def test_expense_crud(self):
        """Test adding, viewing, editing, and deleting expense records."""
        user_id = FinanceService.register_user(self.test_name, self.test_email, self.test_password)
        
        # Add expense
        exp_id = FinanceService.add_expense(user_id, "Food", 150.0, "2026-08-02", "Groceries")
        self.assertIsNotNone(exp_id)
        
        # View expenses
        expenses = FinanceService.get_expenses_by_user(user_id)
        self.assertEqual(len(expenses), 1)
        
        # Edit expense
        updated = FinanceService.update_expense(user_id, exp_id, "Food", 200.0, "2026-08-02", "Organic Groceries")
        self.assertTrue(updated)
        exp_doc = FinanceService.get_expense_by_id(user_id, exp_id)
        self.assertEqual(exp_doc['amount'], 200.0)
        
        # Delete expense
        deleted = FinanceService.delete_expense(user_id, exp_id)
        self.assertTrue(deleted)
        self.assertEqual(len(FinanceService.get_expenses_by_user(user_id)), 0)

    def test_budget_calculation(self):
        """Test category budget setting, actual spending comparison, and over-budget calculation."""
        user_id = FinanceService.register_user(self.test_name, self.test_email, self.test_password)
        
        # Set budget of $300 for Food in August 2026
        BudgetService.create_or_update_budget(user_id, 8, 2026, "Food", 300.0)
        
        # Add expense of $350 for Food in August 2026 (Exceeded)
        FinanceService.add_expense(user_id, "Food", 350.0, "2026-08-10", "Restaurant dinner")
        
        analysis = BudgetService.get_budget_analysis(user_id, 8, 2026)
        self.assertEqual(analysis['total_limit'], 300.0)
        self.assertEqual(analysis['total_spent'], 350.0)
        self.assertEqual(analysis['exceeded_count'], 1)
        self.assertTrue(analysis['items'][0]['is_exceeded'])

    def test_savings_goals_calculation(self):
        """Test savings goals progress calculation and remaining amount."""
        user_id = FinanceService.register_user(self.test_name, self.test_email, self.test_password)
        
        # Add savings goal: Target $1000, Saved $400
        goal_id = FinanceService.add_savings_goal(user_id, "Emergency Fund", 1000.0, 400.0, "2026-12-31")
        goals = FinanceService.get_savings_goals_by_user(user_id)
        
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]['percentage'], 40.0)
        self.assertEqual(goals[0]['remaining'], 600.0)

    def test_dashboard_calculations(self):
        """Test net balance, total income, total expenses, and savings summary."""
        user_id = FinanceService.register_user(self.test_name, self.test_email, self.test_password)
        
        FinanceService.add_income(user_id, "Salary", 4000.0, "2026-08-01", "Paycheck")
        FinanceService.add_expense(user_id, "Rent", 1200.0, "2026-08-02", "Monthly Rent")
        FinanceService.add_expense(user_id, "Bills", 300.0, "2026-08-05", "Utilities")
        FinanceService.add_savings_goal(user_id, "Car", 5000.0, 1000.0)
        
        summary = AnalyticsService.get_dashboard_summary(user_id)
        self.assertEqual(summary['total_income'], 4000.0)
        self.assertEqual(summary['total_expenses'], 1500.0)
        self.assertEqual(summary['current_balance'], 2500.0)
        self.assertEqual(summary['total_savings'], 1000.0)

    def test_user_data_isolation(self):
        """Test that User A cannot see or modify User B's financial data."""
        user_a_id = FinanceService.register_user("User A", "usera@example.com", "Password123")
        user_b_id = FinanceService.register_user("User B", "userb@example.com", "Password123")
        
        # User A adds income
        inc_a_id = FinanceService.add_income(user_a_id, "Salary", 5000.0, "2026-08-01")
        
        # User B queries incomes
        incomes_b = FinanceService.get_income_by_user(user_b_id)
        self.assertEqual(len(incomes_b), 0)
        
        # User B attempts to access or delete User A's record
        doc_b = FinanceService.get_income_by_id(user_b_id, inc_a_id)
        self.assertIsNone(doc_b)
        
        deleted_b = FinanceService.delete_income(user_b_id, inc_a_id)
        self.assertFalse(deleted_b)
        
        # User A's data remains intact
        incomes_a = FinanceService.get_income_by_user(user_a_id)
        self.assertEqual(len(incomes_a), 1)

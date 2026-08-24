from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from finance.database.mongodb import (
    get_users_collection,
    get_income_collection,
    get_expenses_collection,
    get_savings_goals_collection,
    to_object_id,
    format_doc,
    format_docs
)

class FinanceService:

    # ------------------ USER AUTHENTICATION ------------------
    @staticmethod
    def register_user(name, email, password):
        users_col = get_users_collection()
        email = email.strip().lower()
        if users_col.find_one({"email": email}):
            raise ValueError("An account with this email address already exists.")
        
        hashed_password = make_password(password)
        user_doc = {
            "name": name.strip(),
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }
        result = users_col.insert_one(user_doc)
        return str(result.inserted_id)

    @staticmethod
    def authenticate_user(email, password):
        users_col = get_users_collection()
        email = email.strip().lower()
        user = users_col.find_one({"email": email})
        if not user:
            return None
        
        if check_password(password, user["password"]):
            return format_doc(user)
        return None

    @staticmethod
    def get_user_by_id(user_id):
        obj_id = to_object_id(user_id)
        if not obj_id:
            return None
        user = get_users_collection().find_one({"_id": obj_id})
        return format_doc(user)

    # ------------------ INCOME MANAGEMENT ------------------
    @staticmethod
    def add_income(user_id, source, amount, date_str, description=""):
        if amount <= 0:
            raise ValueError("Income amount must be greater than zero.")
        
        date_obj = datetime.strptime(date_str, "%Y-%m-%d") if isinstance(date_str, str) else date_str
        
        doc = {
            "user_id": str(user_id),
            "source": source,
            "amount": float(amount),
            "date": date_obj,
            "description": description.strip(),
            "created_at": datetime.utcnow()
        }
        result = get_income_collection().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_income_by_user(user_id):
        docs = list(get_income_collection().find({"user_id": str(user_id)}).sort("date", -1))
        return format_docs(docs)

    @staticmethod
    def get_income_by_id(user_id, income_id):
        obj_id = to_object_id(income_id)
        doc = get_income_collection().find_one({"_id": obj_id, "user_id": str(user_id)})
        return format_doc(doc)

    @staticmethod
    def update_income(user_id, income_id, source, amount, date_str, description=""):
        if amount <= 0:
            raise ValueError("Income amount must be greater than zero.")
        
        obj_id = to_object_id(income_id)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d") if isinstance(date_str, str) else date_str
        
        result = get_income_collection().update_one(
            {"_id": obj_id, "user_id": str(user_id)},
            {"$set": {
                "source": source,
                "amount": float(amount),
                "date": date_obj,
                "description": description.strip()
            }}
        )
        return result.modified_count > 0

    @staticmethod
    def delete_income(user_id, income_id):
        obj_id = to_object_id(income_id)
        result = get_income_collection().delete_one({"_id": obj_id, "user_id": str(user_id)})
        return result.deleted_count > 0

    # ------------------ EXPENSE MANAGEMENT ------------------
    @staticmethod
    def add_expense(user_id, category, amount, date_str, description=""):
        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")
        
        date_obj = datetime.strptime(date_str, "%Y-%m-%d") if isinstance(date_str, str) else date_str
        
        doc = {
            "user_id": str(user_id),
            "category": category,
            "amount": float(amount),
            "date": date_obj,
            "description": description.strip(),
            "created_at": datetime.utcnow()
        }
        result = get_expenses_collection().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_expenses_by_user(user_id):
        docs = list(get_expenses_collection().find({"user_id": str(user_id)}).sort("date", -1))
        return format_docs(docs)

    @staticmethod
    def get_expense_by_id(user_id, expense_id):
        obj_id = to_object_id(expense_id)
        doc = get_expenses_collection().find_one({"_id": obj_id, "user_id": str(user_id)})
        return format_doc(doc)

    @staticmethod
    def update_expense(user_id, expense_id, category, amount, date_str, description=""):
        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")
        
        obj_id = to_object_id(expense_id)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d") if isinstance(date_str, str) else date_str
        
        result = get_expenses_collection().update_one(
            {"_id": obj_id, "user_id": str(user_id)},
            {"$set": {
                "category": category,
                "amount": float(amount),
                "date": date_obj,
                "description": description.strip()
            }}
        )
        return result.modified_count > 0

    @staticmethod
    def delete_expense(user_id, expense_id):
        obj_id = to_object_id(expense_id)
        result = get_expenses_collection().delete_one({"_id": obj_id, "user_id": str(user_id)})
        return result.deleted_count > 0

    # ------------------ SAVINGS GOALS ------------------
    @staticmethod
    def add_savings_goal(user_id, goal_name, target_amount, saved_amount=0.0, target_date_str=""):
        if target_amount <= 0:
            raise ValueError("Target amount must be greater than zero.")
        if saved_amount < 0:
            raise ValueError("Saved amount cannot be negative.")
        
        target_date = None
        if target_date_str:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d") if isinstance(target_date_str, str) else target_date_str
            
        doc = {
            "user_id": str(user_id),
            "goal_name": goal_name.strip(),
            "target_amount": float(target_amount),
            "saved_amount": float(saved_amount),
            "target_date": target_date,
            "created_at": datetime.utcnow()
        }
        result = get_savings_goals_collection().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_savings_goals_by_user(user_id):
        docs = list(get_savings_goals_collection().find({"user_id": str(user_id)}).sort("created_at", -1))
        formatted = format_docs(docs)
        for g in formatted:
            target = g.get('target_amount', 1)
            saved = g.get('saved_amount', 0)
            g['percentage'] = min(100, round((saved / target) * 100, 1)) if target > 0 else 0
            g['remaining'] = max(0, target - saved)
        return formatted

    @staticmethod
    def get_savings_goal_by_id(user_id, goal_id):
        obj_id = to_object_id(goal_id)
        doc = get_savings_goals_collection().find_one({"_id": obj_id, "user_id": str(user_id)})
        formatted = format_doc(doc)
        if formatted:
            target = formatted.get('target_amount', 1)
            saved = formatted.get('saved_amount', 0)
            formatted['percentage'] = min(100, round((saved / target) * 100, 1)) if target > 0 else 0
            formatted['remaining'] = max(0, target - saved)
        return formatted

    @staticmethod
    def update_savings_goal(user_id, goal_id, goal_name, target_amount, saved_amount, target_date_str=""):
        if target_amount <= 0:
            raise ValueError("Target amount must be greater than zero.")
        if saved_amount < 0:
            raise ValueError("Saved amount cannot be negative.")
        
        obj_id = to_object_id(goal_id)
        target_date = None
        if target_date_str:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d") if isinstance(target_date_str, str) else target_date_str
            
        result = get_savings_goals_collection().update_one(
            {"_id": obj_id, "user_id": str(user_id)},
            {"$set": {
                "goal_name": goal_name.strip(),
                "target_amount": float(target_amount),
                "saved_amount": float(saved_amount),
                "target_date": target_date
            }}
        )
        return result.modified_count > 0

    @staticmethod
    def delete_savings_goal(user_id, goal_id):
        obj_id = to_object_id(goal_id)
        result = get_savings_goals_collection().delete_one({"_id": obj_id, "user_id": str(user_id)})
        return result.deleted_count > 0

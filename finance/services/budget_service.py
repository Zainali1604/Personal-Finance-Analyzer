from datetime import datetime
from finance.database.mongodb import (
    get_budgets_collection,
    get_expenses_collection,
    to_object_id,
    format_doc,
    format_docs
)

class BudgetService:

    @staticmethod
    def create_or_update_budget(user_id, month, year, category, limit_amount):
        if limit_amount <= 0:
            raise ValueError("Budget limit amount must be greater than zero.")
        
        budgets_col = get_budgets_collection()
        month = int(month)
        year = int(year)
        
        existing = budgets_col.find_one({
            "user_id": str(user_id),
            "month": month,
            "year": year,
            "category": category
        })
        
        if existing:
            budgets_col.update_one(
                {"_id": existing["_id"]},
                {"$set": {"limit_amount": float(limit_amount)}}
            )
            return str(existing["_id"])
        else:
            doc = {
                "user_id": str(user_id),
                "month": month,
                "year": year,
                "category": category,
                "limit_amount": float(limit_amount),
                "created_at": datetime.utcnow()
            }
            result = budgets_col.insert_one(doc)
            return str(result.inserted_id)

    @staticmethod
    def get_budgets_by_user(user_id, month=None, year=None):
        query = {"user_id": str(user_id)}
        if month:
            query["month"] = int(month)
        if year:
            query["year"] = int(year)
            
        docs = list(get_budgets_collection().find(query).sort([("year", -1), ("month", -1), ("category", 1)]))
        return format_docs(docs)

    @staticmethod
    def get_budget_by_id(user_id, budget_id):
        obj_id = to_object_id(budget_id)
        doc = get_budgets_collection().find_one({"_id": obj_id, "user_id": str(user_id)})
        return format_doc(doc)

    @staticmethod
    def delete_budget(user_id, budget_id):
        obj_id = to_object_id(budget_id)
        result = get_budgets_collection().delete_one({"_id": obj_id, "user_id": str(user_id)})
        return result.deleted_count > 0

    @staticmethod
    def get_budget_analysis(user_id, month=None, year=None):
        now = datetime.now()
        target_month = int(month) if month else now.month
        target_year = int(year) if year else now.year
        
        budgets = list(get_budgets_collection().find({
            "user_id": str(user_id),
            "month": target_month,
            "year": target_year
        }))
        
        start_date = datetime(target_year, target_month, 1)
        if target_month == 12:
            end_date = datetime(target_year + 1, 1, 1)
        else:
            end_date = datetime(target_year, target_month + 1, 1)
            
        expenses = list(get_expenses_collection().find({
            "user_id": str(user_id),
            "date": {"$gte": start_date, "$lt": end_date}
        }))
        
        # Aggregate spending by category
        spent_by_cat = {}
        for exp in expenses:
            cat = exp.get("category", "Other")
            spent_by_cat[cat] = spent_by_cat.get(cat, 0.0) + float(exp.get("amount", 0.0))
            
        analysis_items = []
        total_limit = 0.0
        total_spent = 0.0
        exceeded_count = 0
        
        for b in budgets:
            cat = b.get("category")
            limit = float(b.get("limit_amount", 0.0))
            spent = spent_by_cat.get(cat, 0.0)
            remaining = limit - spent
            pct = min(100, round((spent / limit) * 100, 1)) if limit > 0 else 0
            is_exceeded = spent > limit
            
            if is_exceeded:
                exceeded_count += 1
                
            total_limit += limit
            total_spent += spent
            
            analysis_items.append({
                "budget_id": str(b["_id"]),
                "category": cat,
                "limit_amount": limit,
                "spent_amount": spent,
                "remaining_amount": max(0, remaining),
                "over_amount": abs(remaining) if is_exceeded else 0.0,
                "percentage": pct,
                "is_exceeded": is_exceeded,
                "status_class": "danger" if is_exceeded else ("warning" if pct >= 80 else "success")
            })
            
        return {
            "month": target_month,
            "year": target_year,
            "items": analysis_items,
            "total_limit": total_limit,
            "total_spent": total_spent,
            "total_remaining": max(0, total_limit - total_spent),
            "exceeded_count": exceeded_count,
            "overall_percentage": min(100, round((total_spent / total_limit) * 100, 1)) if total_limit > 0 else 0
        }

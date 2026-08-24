import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from finance.database.mongodb import (
    get_income_collection,
    get_expenses_collection,
    get_savings_goals_collection
)

class AnalyticsService:

    @staticmethod
    def get_dashboard_summary(user_id):
        """Compute key high-level dashboard metrics for logged-in user."""
        income_docs = list(get_income_collection().find({"user_id": str(user_id)}))
        expense_docs = list(get_expenses_collection().find({"user_id": str(user_id)}))
        savings_docs = list(get_savings_goals_collection().find({"user_id": str(user_id)}))

        total_income = sum(float(i.get('amount', 0)) for i in income_docs)
        total_expenses = sum(float(e.get('amount', 0)) for e in expense_docs)
        current_balance = total_income - total_expenses
        total_saved = sum(float(s.get('saved_amount', 0)) for s in savings_docs)
        total_savings_target = sum(float(s.get('target_amount', 0)) for s in savings_docs)

        # Recent transactions combined
        for i in income_docs:
            i['type'] = 'income'
            i['_id'] = str(i['_id'])
        for e in expense_docs:
            e['type'] = 'expense'
            e['_id'] = str(e['_id'])

        all_tx = income_docs + expense_docs
        all_tx.sort(key=lambda x: x.get('date', datetime.min), reverse=True)
        recent_transactions = all_tx[:7]

        return {
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'current_balance': round(current_balance, 2),
            'total_savings': round(total_saved, 2),
            'savings_target': round(total_savings_target, 2),
            'savings_progress_pct': min(100, round((total_saved / total_savings_target) * 100, 1)) if total_savings_target > 0 else 0,
            'recent_transactions': recent_transactions
        }

    @staticmethod
    def get_spending_analytics(user_id):
        """Use Pandas and NumPy to analyze financial records and format Chart.js data."""
        income_docs = list(get_income_collection().find({"user_id": str(user_id)}))
        expense_docs = list(get_expenses_collection().find({"user_id": str(user_id)}))

        # Defaults if no data
        category_chart_data = {"labels": [], "data": []}
        monthly_chart_data = {"labels": [], "income_data": [], "expense_data": []}
        savings_trend_data = {"labels": [], "data": []}
        
        highest_category = {"category": "N/A", "amount": 0.0}
        lowest_category = {"category": "N/A", "amount": 0.0}
        avg_monthly_spending = 0.0
        
        # 1. Category-wise Expenses Analysis via Pandas
        if expense_docs:
            df_exp = pd.DataFrame(expense_docs)
            df_exp['amount'] = df_exp['amount'].astype(float)
            
            cat_grouped = df_exp.groupby('category')['amount'].sum().reset_index()
            cat_grouped = cat_grouped.sort_values(by='amount', ascending=False)
            
            category_chart_data = {
                "labels": cat_grouped['category'].tolist(),
                "data": cat_grouped['amount'].round(2).tolist()
            }
            
            if not cat_grouped.empty:
                highest_category = {
                    "category": cat_grouped.iloc[0]['category'],
                    "amount": round(float(cat_grouped.iloc[0]['amount']), 2)
                }
                lowest_category = {
                    "category": cat_grouped.iloc[-1]['category'],
                    "amount": round(float(cat_grouped.iloc[-1]['amount']), 2)
                }

        # 2. Monthly Income & Expenses via Pandas Time Series Analysis
        all_records = []
        for inc in income_docs:
            dt = inc.get('date')
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d")
            all_records.append({
                'month_year': dt.strftime('%b %Y'),
                'period': dt.strftime('%Y-%m'),
                'type': 'income',
                'amount': float(inc.get('amount', 0))
            })
            
        for exp in expense_docs:
            dt = exp.get('date')
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d")
            all_records.append({
                'month_year': dt.strftime('%b %Y'),
                'period': dt.strftime('%Y-%m'),
                'type': 'expense',
                'amount': float(exp.get('amount', 0))
            })

        if all_records:
            df_all = pd.DataFrame(all_records)
            df_pivot = df_all.pivot_table(
                index=['period', 'month_year'],
                columns='type',
                values='amount',
                aggfunc='sum',
                fill_value=0.0
            ).reset_index()
            
            df_pivot = df_pivot.sort_values('period')
            
            if 'income' not in df_pivot.columns:
                df_pivot['income'] = 0.0
            if 'expense' not in df_pivot.columns:
                df_pivot['expense'] = 0.0

            # NumPy calculation for average monthly spending
            expense_arr = np.array(df_pivot['expense'].values)
            if len(expense_arr) > 0:
                avg_monthly_spending = float(np.mean(expense_arr))

            df_pivot['savings_delta'] = df_pivot['income'] - df_pivot['expense']
            df_pivot['cumulative_savings'] = np.cumsum(df_pivot['savings_delta'].values)

            monthly_chart_data = {
                "labels": df_pivot['month_year'].tolist(),
                "income_data": df_pivot['income'].round(2).tolist(),
                "expense_data": df_pivot['expense'].round(2).tolist()
            }

            savings_trend_data = {
                "labels": df_pivot['month_year'].tolist(),
                "data": df_pivot['cumulative_savings'].round(2).tolist()
            }

        return {
            "category_chart": category_chart_data,
            "monthly_chart": monthly_chart_data,
            "savings_trend_chart": savings_trend_data,
            "highest_category": highest_category,
            "lowest_category": lowest_category,
            "avg_monthly_spending": round(avg_monthly_spending, 2)
        }

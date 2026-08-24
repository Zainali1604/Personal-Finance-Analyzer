import os
import csv
from datetime import datetime
import pandas as pd
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from finance.database.mongodb import (
    get_income_collection,
    get_expenses_collection,
    get_budgets_collection,
    get_savings_goals_collection,
    format_docs
)
from finance.services.budget_service import BudgetService

class ReportService:

    @staticmethod
    def get_monthly_report_data(user_id, month, year):
        month = int(month)
        year = int(year)
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        income_docs = list(get_income_collection().find({
            "user_id": str(user_id),
            "date": {"$gte": start_date, "$lt": end_date}
        }))
        
        expense_docs = list(get_expenses_collection().find({
            "user_id": str(user_id),
            "date": {"$gte": start_date, "$lt": end_date}
        }))

        total_income = sum(float(i.get('amount', 0)) for i in income_docs)
        total_expenses = sum(float(e.get('amount', 0)) for e in expense_docs)
        total_savings = total_income - total_expenses
        total_transactions = len(income_docs) + len(expense_docs)

        # Highest expense category
        highest_cat = "None"
        if expense_docs:
            df_exp = pd.DataFrame(expense_docs)
            df_exp['amount'] = df_exp['amount'].astype(float)
            cat_sum = df_exp.groupby('category')['amount'].sum().reset_index()
            cat_sum = cat_sum.sort_values(by='amount', ascending=False)
            if not cat_sum.empty:
                highest_cat = f"{cat_sum.iloc[0]['category']} (${cat_sum.iloc[0]['amount']:.2f})"

        # Budget analysis for month
        budget_analysis = BudgetService.get_budget_analysis(user_id, month, year)

        # Savings Goals overall
        savings_docs = list(get_savings_goals_collection().find({"user_id": str(user_id)}))
        formatted_savings = format_docs(savings_docs)

        # Format item lists for report
        formatted_income = format_docs(income_docs)
        formatted_expenses = format_docs(expense_docs)

        return {
            "month": month,
            "year": year,
            "month_name": start_date.strftime("%B"),
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "total_savings": round(total_savings, 2),
            "total_transactions": total_transactions,
            "highest_expense_category": highest_cat,
            "budget_analysis": budget_analysis,
            "savings_goals": formatted_savings,
            "income_list": formatted_income,
            "expense_list": formatted_expenses
        }

    @staticmethod
    def generate_csv_report(report_data):
        """Generate a CSV file for the monthly report."""
        filename = f"report_{report_data['month_name']}_{report_data['year']}.csv"
        filepath = os.path.join(settings.REPORTS_ROOT, filename)
        
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Personal Finance Monthly Report", f"{report_data['month_name']} {report_data['year']}"])
            writer.writerow([])
            writer.writerow(["SUMMARY METRICS"])
            writer.writerow(["Total Income", f"${report_data['total_income']:.2f}"])
            writer.writerow(["Total Expenses", f"${report_data['total_expenses']:.2f}"])
            writer.writerow(["Net Savings", f"${report_data['total_savings']:.2f}"])
            writer.writerow(["Total Transactions", report_data['total_transactions']])
            writer.writerow(["Highest Expense Category", report_data['highest_expense_category']])
            writer.writerow([])
            
            writer.writerow(["INCOME RECORDS"])
            writer.writerow(["Date", "Source", "Amount", "Description"])
            for inc in report_data['income_list']:
                dt = inc['date'].strftime('%Y-%m-%d') if isinstance(inc['date'], datetime) else str(inc['date'])[:10]
                writer.writerow([dt, inc.get('source'), f"${inc.get('amount'):.2f}", inc.get('description')])
                
            writer.writerow([])
            writer.writerow(["EXPENSE RECORDS"])
            writer.writerow(["Date", "Category", "Amount", "Description"])
            for exp in report_data['expense_list']:
                dt = exp['date'].strftime('%Y-%m-%d') if isinstance(exp['date'], datetime) else str(exp['date'])[:10]
                writer.writerow([dt, exp.get('category'), f"${exp.get('amount'):.2f}", exp.get('description')])
                
        return filepath, filename

    @staticmethod
    def generate_pdf_report(report_data):
        """Generate a styled PDF document for the monthly report."""
        filename = f"report_{report_data['month_name']}_{report_data['year']}.pdf"
        filepath = os.path.join(settings.REPORTS_ROOT, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=12
        )
        
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=20
        )
        
        h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=15,
            spaceAfter=10
        )

        elements = []
        elements.append(Paragraph(f"Monthly Financial Report", title_style))
        elements.append(Paragraph(f"Period: <b>{report_data['month_name']} {report_data['year']}</b>", subtitle_style))
        elements.append(Spacer(1, 10))

        # Summary Table
        summary_data = [
            ["Metric", "Value"],
            ["Total Income", f"${report_data['total_income']:,.2f}"],
            ["Total Expenses", f"${report_data['total_expenses']:,.2f}"],
            ["Net Monthly Savings", f"${report_data['total_savings']:,.2f}"],
            ["Total Transactions", str(report_data['total_transactions'])],
            ["Highest Expense Category", report_data['highest_expense_category']]
        ]
        
        t_summary = Table(summary_data, colWidths=[250, 250])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ]))
        elements.append(t_summary)
        elements.append(Spacer(1, 20))

        # Budget Overview Section
        elements.append(Paragraph("Budget Analysis", h2_style))
        budget_items = report_data['budget_analysis']['items']
        if budget_items:
            b_data = [["Category", "Budget Limit", "Spent Amount", "Status"]]
            for item in budget_items:
                status_str = "EXCEEDED" if item['is_exceeded'] else "OK"
                b_data.append([
                    item['category'],
                    f"${item['limit_amount']:,.2f}",
                    f"${item['spent_amount']:,.2f}",
                    status_str
                ])
            t_budget = Table(b_data, colWidths=[150, 125, 125, 100])
            t_budget.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t_budget)
        else:
            elements.append(Paragraph("No category budgets set for this month.", styles['Normal']))

        doc.build(elements)
        return filepath, filename

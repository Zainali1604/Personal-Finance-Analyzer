# Personal Finance Analyzer — Complete Django + MongoDB Project

An end-to-end **Personal Finance Analyzer** web application built with **Python**, **Django**, **MongoDB**, **Pandas**, **NumPy**, **Bootstrap 5**, and **Chart.js**.

Designed to help users record income and expenses, set monthly category budgets with automated warning alerts, track savings goals, inspect spending analytics, and export downloadable monthly reports (CSV/PDF).

---

## 🌟 Key Features

* **User Authentication & Isolation**: Registration, login, logout, password hashing, and strict user data isolation.
* **Income Management**: Add, view, edit, and delete earnings by source (Salary, Freelancing, Business, etc.).
* **Expense Management**: Add, view, edit, and delete expenditures by category (Food, Travel, Bills, Rent, etc.).
* **Budget Planning**: Set monthly spending limits per category, track spent vs remaining amounts, and trigger warnings when limits are exceeded.
* **Savings Goals**: Create target savings goals with completion percentage indicators and remaining balance tracking.
* **Dashboard Summary**: Real-time summary cards for Total Income, Total Expenses, Current Balance, Total Savings, Budget Alerts, and Recent Transactions.
* **Pandas & NumPy Spending Analytics**: Dynamic data manipulation computing highest/lowest spending categories, average monthly spending, and cumulative savings trends.
* **Interactive Visualizations**: Doughnut charts for category breakdown, Bar charts for income vs expenses, and Line charts for savings trends powered by **Chart.js**.
* **Monthly Reports**: Filter report summaries by month and year, and export downloadable **CSV** and styled **PDF** reports.
* **Cloud Deployment Ready**: Built-in `render.yaml`, `Procfile`, `build.sh`, and WhiteNoise static files setup for one-click Render deployment.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.13, Django 5.2, PyMongo |
| **Database** | MongoDB (Local / MongoDB Atlas Cloud) |
| **Data Analysis** | Pandas, NumPy |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5, FontAwesome |
| **Charts & Reports** | Chart.js, ReportLab (PDF export) |
| **WSGI / Deployment** | Gunicorn, WhiteNoise |

---

## 📁 Project Folder Structure

```text
Personal-Finance-Analyzer/
│
├── manage.py                  # Django administrative script
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation & viva guide
├── Procfile                   # Process file for Render / Heroku
├── render.yaml                # Render Blueprint deployment config
├── build.sh                   # Deployment build script
├── .env                       # Environment secrets (ignored by git)
├── .env.example               # Template environment configuration
├── .gitignore                 # Version control ignores
│
├── config/                    # Core Django configuration
│   ├── __init__.py
│   ├── settings.py            # Global settings & MongoDB environment setup
│   ├── urls.py                # Main URL routing
│   ├── asgi.py
│   └── wsgi.py
│
├── finance/                   # Django Application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py                # App config & MongoDB startup index init
│   ├── models.py              # Docstring reference for MongoDB collections
│   ├── views.py               # Request handlers & views
│   ├── urls.py                # App URL routing
│   ├── forms.py               # Server-side validation forms
│   ├── tests.py               # Unit test suite
│   │
│   ├── database/              # MongoDB DAO Layer
│   │   ├── __init__.py
│   │   └── mongodb.py         # PyMongo client, collection getters, and indexes
│   │
│   ├── services/              # Business Logic Services
│   │   ├── __init__.py
│   │   ├── finance_service.py # User auth, income/expense/savings CRUD
│   │   ├── budget_service.py  # Monthly budget analysis & limit warnings
│   │   ├── analytics_service.py # Pandas & NumPy aggregations
│   │   └── report_service.py  # Monthly report generation (CSV & PDF)
│   │
│   ├── templates/             # HTML Templates
│   │   └── finance/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── dashboard.html
│   │       ├── income.html
│   │       ├── expenses.html
│   │       ├── add_expense.html
│   │       ├── budget.html
│   │       ├── savings_goals.html
│   │       ├── analytics.html
│   │       └── reports.html
│   │
│   └── static/                # Static CSS & JS Assets
│       └── finance/
│           ├── css/
│           │   └── style.css
│           ├── js/
│           │   └── script.js
│           └── images/
│
├── media/                     # User uploads directory
└── reports/                   # Generated PDF and CSV reports directory
```

---

## 🗄️ MongoDB Database Collections Schema

1. **`users`**: `_id`, `name`, `email` (unique index), `password` (hashed), `created_at`
2. **`income`**: `_id`, `user_id`, `source`, `amount`, `date`, `description`, `created_at`
3. **`expenses`**: `_id`, `user_id`, `category`, `amount`, `date`, `description`, `created_at`
4. **`budgets`**: `_id`, `user_id`, `month`, `year`, `category`, `limit_amount`, `created_at`
5. **`savings_goals`**: `_id`, `user_id`, `goal_name`, `target_amount`, `saved_amount`, `target_date`, `created_at`

---

## ⚙️ Environment Variables Setup

Create a `.env` file in the root directory:

```env
SECRET_KEY=django-insecure-personal-finance-analyzer-secret-key-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=personal_finance_db
```

---

## 🚀 Local Installation & Execution Guide

### Step 1: Clone or Navigate to Project Directory
```bash
cd C:\Users\Zainalipatel\.gemini\antigravity\scratch\Personal-Finance-Analyzer
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Ensure MongoDB Service is Running
Start your local MongoDB service (`mongod`) or update `MONGO_URI` in `.env` to point to MongoDB Atlas.

### Step 4: Run Django Migrations & Server
```bash
python manage.py migrate
python manage.py runserver
```

Open your browser and navigate to: `http://127.0.0.1:8000/`

---

## ☁️ How to Deploy on Render to Get a Live Deployment URL (`*.onrender.com`)

To get a live public link like `https://personal-finance-analyzer-app.onrender.com`:

### Step 1: Create a Free MongoDB Atlas Database
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign up for a free M0 cluster.
2. Create a database user and copy your Connection String (e.g. `mongodb+srv://username:password@cluster0.mongodb.net/?retryWrites=true&w=majority`).

### Step 2: Push Project Code to GitHub
1. Initialize Git and commit code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Personal Finance Analyzer"
   ```
2. Push your repository to GitHub.

### Step 3: Create Web Service on Render
1. Log in to [Render](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Select Environment: **Python**.
5. Set Build Command: `./build.sh`
6. Set Start Command: `gunicorn config.wsgi:application`
7. In **Environment Variables**, add:
   * `MONGO_URI`: Your MongoDB Atlas Connection String
   * `MONGO_DB_NAME`: `personal_finance_db`
   * `SECRET_KEY`: (Click generate)
   * `DEBUG`: `False`
   * `ALLOWED_HOSTS`: `.onrender.com`
8. Click **Create Web Service**. Render will build and host your app live!

---

## 🧪 Testing Procedure

Run the unit test suite covering registration, auth, income/expense CRUD, budget warnings, savings progress, and user data isolation:

```bash
python manage.py test finance
```

---

## 🎓 Viva Explanation & Architecture Overview

* **Why PyMongo instead of Djongo?**
  PyMongo provides native, high-performance, robust MongoDB integration compatible with modern Python 3.13 and Django 5.x without requiring ORM monkey-patching.

* **How is User Data Isolation Enforced?**
  Every service call explicitly passes `user_id=request.session['user_id']` into MongoDB `find()`, `update_one()`, and `delete_one()` queries, ensuring users can only read or write their own documents.

* **How is Pandas & NumPy Used?**
  Pandas DataFrames group and aggregate spending entries by category and month, while NumPy computes mean monthly expenditure and cumulative savings arrays.

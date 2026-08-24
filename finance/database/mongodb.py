import os
from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from django.conf import settings

client = None
db = None

def get_db():
    global client, db
    if db is None:
        mongo_uri = getattr(settings, 'MONGO_URI', 'mongodb://localhost:27017/')
        db_name = getattr(settings, 'MONGO_DB_NAME', 'personal_finance_db')
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            db = client[db_name]
        except Exception as e:
            print(f"[MongoDB Connection Error]: {e}")
            raise e
    return db

def get_users_collection():
    return get_db()['users']

def get_income_collection():
    return get_db()['income']

def get_expenses_collection():
    return get_db()['expenses']

def get_budgets_collection():
    return get_db()['budgets']

def get_savings_goals_collection():
    return get_db()['savings_goals']

def init_db():
    """Create indexes for MongoDB collections."""
    try:
        users = get_users_collection()
        users.create_index([("email", ASCENDING)], unique=True)
        
        income = get_income_collection()
        income.create_index([("user_id", ASCENDING), ("date", ASCENDING)])
        
        expenses = get_expenses_collection()
        expenses.create_index([("user_id", ASCENDING), ("date", ASCENDING)])
        
        budgets = get_budgets_collection()
        budgets.create_index([("user_id", ASCENDING), ("month", ASCENDING), ("year", ASCENDING)])
        
        savings = get_savings_goals_collection()
        savings.create_index([("user_id", ASCENDING)])
        
        print("[MongoDB] Indexes initialized successfully.")
    except Exception as e:
        print(f"[MongoDB Init Error]: {e}")

def to_object_id(id_str):
    """Safely convert string or ObjectId to ObjectId."""
    if isinstance(id_str, ObjectId):
        return id_str
    try:
        return ObjectId(str(id_str))
    except Exception:
        return None

def format_doc(doc):
    """Convert MongoDB document ObjectId fields to string for template / JSON compatibility."""
    if not doc:
        return doc
    doc['_id'] = str(doc['_id'])
    if 'user_id' in doc and isinstance(doc['user_id'], ObjectId):
        doc['user_id'] = str(doc['user_id'])
    return doc

def format_docs(docs):
    """Format list of MongoDB documents."""
    return [format_doc(d) for d in docs]

from django.apps import AppConfig

class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'

    def ready(self):
        # Ensure MongoDB indexes on app startup
        try:
            from finance.database.mongodb import init_db
            init_db()
        except Exception as e:
            print(f"[MongoDB Startup Warning]: {e}")

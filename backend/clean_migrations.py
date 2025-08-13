# clean_migrations.py
import os, shutil

# عدّل القائمة دي حسب تطبيقاتك المحلية
APPS = [
    "core",
    "customers",
    "notifications",
    "accounts",
    "approvals",
    "shared",
    "suppliers",
    "inventory",
]

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# اختياري: امسح قاعدة البيانات إن وُجدت
REMOVE_DB = False
DB_PATH = os.path.join(PROJECT_ROOT, "db.sqlite3")

def clean_app_migrations(app_path):
    mig_dir = os.path.join(app_path, "migrations")
    if not os.path.isdir(mig_dir):
        return 0
    deleted = 0
    # امسح __pycache__
    for root, dirs, files in os.walk(mig_dir):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"), ignore_errors=True)
    # امسح كل .py و .pyc ما عدا __init__.py
    for root, dirs, files in os.walk(mig_dir):
        for f in files:
            if f == "__init__.py":
                continue
            if f.endswith(".py") or f.endswith(".pyc"):
                try:
                    os.remove(os.path.join(root, f))
                    deleted += 1
                except FileNotFoundError:
                    pass
    # تأكد وجود __init__.py
    init_file = os.path.join(mig_dir, "__init__.py")
    if not os.path.exists(init_file):
        open(init_file, "a").close()
    return deleted

def main():
    total = 0
    for app in APPS:
        app_path = os.path.join(PROJECT_ROOT, app)
        if os.path.isdir(app_path):
            total += clean_app_migrations(app_path)
    if REMOVE_DB and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed DB: {DB_PATH}")
    print(f"Done. Deleted {total} migration files/pyc across {len(APPS)} apps.")

if __name__ == "__main__":
    main()

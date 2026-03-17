"""
examples/demo_project/app.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A fake application that uses environment variables in various ways.
Run `envguard scan examples/demo_project` from the repo root to see
envguard in action.
"""

import os

# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------
DATABASE_URL = os.environ["DATABASE_URL"]          # required, no default
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5")) # required; int inferred from int()
DB_TIMEOUT   = int(os.getenv("DB_TIMEOUT", "30"))  # optional

# -------------------------------------------------------------------
# Redis / cache
# -------------------------------------------------------------------
REDIS_URL     = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL     = int(os.getenv("CACHE_TTL", "300"))

# -------------------------------------------------------------------
# Auth & secrets
# -------------------------------------------------------------------
SECRET_KEY    = os.environ["SECRET_KEY"]           # required; secret inferred from name
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
API_TOKEN     = os.environ["API_TOKEN"]            # required

# -------------------------------------------------------------------
# App settings
# -------------------------------------------------------------------
DEBUG         = os.getenv("DEBUG", "false")        # bool inferred from name
LOG_LEVEL     = os.getenv("LOG_LEVEL", "INFO")
APP_PORT      = int(os.getenv("APP_PORT", "8080")) # int inferred from int()
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")

# -------------------------------------------------------------------
# External services
# -------------------------------------------------------------------
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.environ["SMTP_USER"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]        # secret
ADMIN_EMAIL   = os.getenv("ADMIN_EMAIL", "admin@example.com")

# -------------------------------------------------------------------
# Storage
# -------------------------------------------------------------------
S3_BUCKET     = os.environ["S3_BUCKET"]
AWS_ACCESS_KEY_ID     = os.environ["AWS_ACCESS_KEY_ID"]     # secret
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"] # secret
UPLOAD_PATH   = os.getenv("UPLOAD_PATH", "/tmp/uploads")    # path inferred from name

# -------------------------------------------------------------------
# Feature flags
# -------------------------------------------------------------------
ENABLE_SIGNUP    = os.getenv("ENABLE_SIGNUP", "true")    # bool inferred from name
USE_CDN          = os.getenv("USE_CDN", "false")         # bool
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false")# bool

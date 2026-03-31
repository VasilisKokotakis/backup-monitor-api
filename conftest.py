"""
Root conftest — sets environment variables before any app module is imported.
pytest loads this file before collecting tests, so Settings() sees these values.
In CI, these would be set as pipeline secrets instead.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("RATELIMIT_ENABLED", "false")

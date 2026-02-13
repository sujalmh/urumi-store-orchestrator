import sys
import os

# Add backend directory to sys.path especially if run from scripts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base
from app.db.session import engine
from app.models.user import UserORM
from app.models.store import StoreORM
from app.models.audit_log import AuditLogORM
from app.models.rate_limit import RateLimitORM

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    init_db()

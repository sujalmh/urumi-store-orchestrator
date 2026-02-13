import sys
import os
from sqlalchemy import inspect, text

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine

def inspect_db():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Existing tables:", tables)
    
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT * FROM pg_indexes WHERE schemaname = 'public';"))
            print("\nExisting indexes:")
            for row in result:
                print(row)
        except Exception as e:
            print(f"Error querying indexes: {e}")

if __name__ == "__main__":
    inspect_db()

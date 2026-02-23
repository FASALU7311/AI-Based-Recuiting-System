from app import app, db
from sqlalchemy import text, inspect

def migrate_add_video_count():
    """
    Adds the 'video_count' column to the Interview table
    without deleting existing data.
    """
    with app.app_context():
        print("Checking database schema...")
        
        # Get the underlying database connection
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('interview')]
        
        if 'video_count' in columns:
            print("✅ Column 'video_count' already exists. No action needed.")
        else:
            print("📝 Adding 'video_count' column to Interview table...")
            
            # Use raw SQL to add the column (Safe for SQLite)
            # SQLite syntax: ALTER TABLE table_name ADD COLUMN column_name TYPE
            sql = text("ALTER TABLE interview ADD COLUMN video_count INTEGER DEFAULT 0")
            
            db.session.execute(sql)
            db.session.commit()
            
            print("✅ Migration successful! 'video_count' added.")

if __name__ == "__main__":
    migrate_add_video_count()
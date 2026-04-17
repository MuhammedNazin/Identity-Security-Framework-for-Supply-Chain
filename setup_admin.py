import os
from app import app
from models import db, User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Get the database path
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        db_path = db_uri.replace('sqlite:///', '')
        
        # Ensure path is absolute if relative
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.instance_path, db_path)
            
        print(f"Target Database Path: {db_path}")
        
        # Explicitly remove the DB file to force fresh schema
        if os.path.exists(db_path):
            print(f"Removing old database at {db_path}...")
            # We must close any sessions first
            db.session.remove()
            db.engine.dispose()
            try:
                os.remove(db_path)
                print("Old database removed.")
            except Exception as e:
                print(f"Error removing database: {e}")
        
        # Create fresh tables
        db.create_all()
        print("Fresh database tables created.")
        
        email = "25879@yenepoya.edu.in"
        print(f"Creating/Updating admin user: {email}")
        
        new_user = User(
            username="NachuAdmin",
            email=email,
            password_hash=generate_password_hash("Nachu@123", method='scrypt'),
            role="Manager"
        )
        db.session.add(new_user)
        db.session.commit()
        print("Success: Admin user is ready in the fresh database.")

if __name__ == "__main__":
    create_admin()

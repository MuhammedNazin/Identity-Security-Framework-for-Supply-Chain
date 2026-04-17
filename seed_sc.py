from app import app
from models import db, User, Cargo
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():
        print("Resetting Supply Chain DB...")
        db.drop_all()
        db.create_all()
        
        admin_email = "25879@yenepoya.edu.in"
        admin = User(username="NachuAdmin", email=admin_email, 
                       password_hash=generate_password_hash("Nachu@123", method='scrypt'), 
                       role="Manager")
        
        db.session.add(admin)
        db.session.commit()
        
        # Cargo - Encrypted via model properties automatically
        c1 = Cargo(tracking_number="TC-99812", content="High-Precision Optic Sensors", 
                     origin="Tokyo, JP", destination="Berlin, DE", status="In Transit")
        c2 = Cargo(tracking_number="TC-99813", content="Industrial Titanium Alloy", 
                     origin="Sydney, AU", destination="Detroit, US", status="Held")
        
        db.session.add_all([c1, c2])
        db.session.commit()
        print("Supply Chain Seeding Successful.")

if __name__ == "__main__":
    seed()

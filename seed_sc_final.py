import uuid
import sys
from app import app
from models import db, User, Cargo
from werkzeug.security import generate_password_hash

# Mock coordinates for realistic geo-telemetry mapping
CITY_COORDS = {
    "Tokyo": [35.6762, 139.6503],
    "Berlin": [52.5200, 13.4050],
    "New York": [40.7128, -74.0060],
    "London": [51.5074, -0.1278],
    "Singapore": [1.3521, 103.8198],
    "Mumbai": [19.0760, 72.8777]
}

def seed_db():
    with app.app_context():
        # Clean current database
        db.drop_all()
        db.create_all()

        # Seed Users
        supplier = User(
            username="Test Supplier",
            email="Mohammadnazin7@gmail.com",
            password_hash=generate_password_hash("test", method='scrypt'),
            pass_prefix="te", pass_suffix="st",
            role="Supplier"
        )
        db.session.add(supplier)

        manager = User(
            username="Global Operations",
            email="25879@yenepoya.edu.in",
            password_hash=generate_password_hash("Nachu@123", method='scrypt'),
            pass_prefix="Na", pass_suffix="23",
            role="Manager"
        )
        db.session.add(manager)

        logistics = User(
            username="Test Logistics",
            email="Muhammednazin41@gmail.com",
            password_hash=generate_password_hash("test", method='scrypt'),
            pass_prefix="te", pass_suffix="st",
            role="Logistics"
        )
        db.session.add(logistics)
        db.session.commit()

        # Generate seed cargo
        default_flows = [
            ("Tokyo", "Berlin", "Industrial Tech Paks", 120),
            ("New York", "London", "Medical Equipment", 400),
            ("Singapore", "Mumbai", "Consumer Electronics", 650),
            ("Berlin", "New York", "Automotive Parts", 1500)
        ]

        print("Seeding new expanded High-Precision Supply Chain db...")
        for origin, dest, item, qty in default_flows:
            o_lat, o_lng = CITY_COORDS[origin]
            d_lat, d_lng = CITY_COORDS[dest]
            
            cargo = Cargo(
                tracking_number=f"TRK-{uuid.uuid4().hex[:8].upper()}",
                item_name=item,
                quantity=qty,
                weight=qty * 1.5,
                origin=origin,
                destination=dest,
                origin_lat=o_lat,
                origin_lng=o_lng,
                dest_lat=d_lat,
                dest_lng=d_lng,
                content=f"High Priority Route {origin}->{dest}",
                status="In Transit",
                supplier_id=supplier.id
            )
            db.session.add(cargo)
        
        db.session.commit()
        print("Done. Database has been restructured and seeded with physical locations.")

if __name__ == "__main__":
    seed_db()

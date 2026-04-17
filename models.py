from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from security_utils import shield

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True) # Nullable for Google-only users
    role = db.Column(db.String(50), nullable=False) # Supplier, Manager, Logistics
    
    # New Fields for    
    # Security Factors
    pass_prefix = db.Column(db.String(2), nullable=True)
    pass_suffix = db.Column(db.String(2), nullable=True)
    google_id = db.Column(db.String(150), unique=True, nullable=True)
    totp_secret = db.Column(db.String(32), nullable=True)
    is_2fa_enabled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username} - {self.role}>'

from datetime import datetime

class Cargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100), unique=True, nullable=False)
    item_name = db.Column(db.String(200), nullable=False, default="General Cargo")
    quantity = db.Column(db.Integer, default=1)
    weight = db.Column(db.Float, default=0.0) # in kg
    
    _content = db.Column('content', db.String(512), nullable=False) # Encrypted
    _origin = db.Column('origin', db.String(512)) # Encrypted
    _destination = db.Column('destination', db.String(512)) # Encrypted
    
    # Geo-Telemetry for Logistics Map
    origin_lat = db.Column(db.Float)
    origin_lng = db.Column(db.Float)
    dest_lat = db.Column(db.Float)
    dest_lng = db.Column(db.Float)
    
    status = db.Column(db.String(50), default="In Transit") # In Transit, Delivered, Held
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    supplier = db.relationship('User', backref=db.backref('shipments', lazy=True))

    @property
    def content(self):
        return shield.decrypt_data(self._content)

    @content.setter
    def content(self, value):
        self._content = shield.encrypt_data(value)

    @property
    def origin(self):
        return shield.decrypt_data(self._origin)

    @origin.setter
    def origin(self, value):
        self._origin = shield.encrypt_data(value)

    @property
    def destination(self):
        return shield.decrypt_data(self._destination)

    @destination.setter
    def destination(self, value):
        self._destination = shield.encrypt_data(value)

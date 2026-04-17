from flask import Flask, render_template, redirect, url_for, request, flash, abort, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from models import db, User, Cargo
from functools import wraps
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import pyotp
import qrcode
import io
import base64
import os
from dotenv import load_dotenv

# Load environment variables from the root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SC_SECRET_KEY', 'supply-chain-secret-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///supply_chain_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.getenv('SC_GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('SC_GOOGLE_CLIENT_SECRET')

db.init_app(app)
csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["300 per day", "100 per hour"],
    storage_uri="memory://"
)

# Security Headers (Anti-Hack)
csp = {
    'default-src': '\'self\'',
    'script-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'https://cdn.jsdelivr.net',
        'https://unpkg.com'
    ],
    'style-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'https://fonts.googleapis.com',
        'https://unpkg.com'
    ],
    'font-src': [
        '\'self\'',
        'https://fonts.gstatic.com'
    ],
    'img-src': ['\'self\'', 'data:', 'https://*.tile.openstreetmap.org', 'https://unpkg.com', 'https://*.basemaps.cartocdn.com']
}
Talisman(app, content_security_policy=csp)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            # Universal access for Managers
            if current_user.role == 'Manager':
                return f(*args, **kwargs)
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', 'error')
            return redirect(url_for('signup'))

        # Prevent unauthorized Manager registration
        if role == 'Manager':
            flash('The Manager role is restricted to pre-authorized administrators.', 'error')
            return redirect(url_for('signup'))

        pass_prefix = None
        pass_suffix = None
        if password:
            padded_pass = (password * 4)[:4]
            if len(password) >= 4:
                pass_prefix = password[:2]
                pass_suffix = password[-2:]
            else:
                pass_prefix = padded_pass[:2]
                pass_suffix = padded_pass[-2:]

        new_user = User(
            username=username, 
            email=email, 
            password_hash=generate_password_hash(password, method='scrypt'),
            pass_prefix=pass_prefix,
            pass_suffix=pass_suffix,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Login failed. Check your credentials.', 'error')
            return redirect(url_for('login'))

        # Check for 2FA
        if user.is_2fa_enabled:
            session['pending_2fa_user_id'] = user.id
            return redirect(url_for('verify_2fa'))

        login_user(user)
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    if not user_info:
        flash('Google authentication failed.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(google_id=user_info['sub']).first()
    if not user:
        # Check if user exists by email
        user = User.query.filter_by(email=user_info['email']).first()
        if user:
            user.google_id = user_info['sub']
            db.session.commit()
        else:
            # 🏛️ Institutional Role Mapping
            MANAGER_EMAILS = ['25879@yenepoya.edu.in']
            LOGISTICS_EMAILS = ['Muhammednazin41@gmail.com']
            SUPPLIER_EMAILS = ['Mohammadnazin7@gmail.com']

            if user_info['email'] in MANAGER_EMAILS:
                assigned_role = 'Manager'
            elif user_info['email'] in LOGISTICS_EMAILS:
                assigned_role = 'Logistics'
            elif user_info['email'] in SUPPLIER_EMAILS:
                assigned_role = 'Supplier'
            else:
                assigned_role = 'Supplier' # Default role for new partners

            # Create new user via Google
            user = User(
                username=user_info['name'],
                email=user_info['email'],
                google_id=user_info['sub'],
                role=assigned_role
            )
            db.session.add(user)
            db.session.commit()
            flash('Account created via Google!', 'success')

    if user.is_2fa_enabled:
        session['pending_2fa_user_id'] = user.id
        return redirect(url_for('verify_2fa'))

    login_user(user)
    return redirect(url_for('dashboard'))

# ═════ PASSWORD RESET PIPELINE ═════

@app.route('/reset-password', endpoint='reset_request', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Origin unknown. Signal dropped.', 'error')
            return redirect(url_for('reset_request'))
        
        session['reset_user_id'] = user.id
        
        if user.is_2fa_enabled:
            return redirect(url_for('reset_mfa'))
        else:
            return redirect(url_for('reset_fallback'))
    return render_template('reset_request.html')

@app.route('/reset/mfa', endpoint='reset_mfa', methods=['GET', 'POST'])
def reset_mfa():
    user_id = session.get('reset_user_id')
    if not user_id:
        return redirect(url_for('reset_request'))
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        otp = request.form.get('otp_code')
        if pyotp.TOTP(user.totp_secret).verify(otp):
            session['reset_authorized'] = True
            return redirect(url_for('reset_new'))
        else:
            flash('Invalid MFA code.', 'error')
    
    # Reuse the 2FA template for MFA entry
    return render_template('verify_2fa.html', reauth=True)

@app.route('/reset/fallback', endpoint='reset_fallback', methods=['GET', 'POST'])
def reset_fallback():
    user_id = session.get('reset_user_id')
    if not user_id:
        return redirect(url_for('reset_request'))
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        prefix = request.form.get('prefix')
        suffix = request.form.get('suffix')
        
        match_prefix = user.pass_prefix == prefix if user.pass_prefix else True
        match_suffix = user.pass_suffix == suffix if user.pass_suffix else True
        
        if match_prefix and match_suffix:
            session['reset_authorized'] = True
            return redirect(url_for('reset_new'))
        else:
            flash('Verification failed. Invalid fragments.', 'error')
    return render_template('reset_fallback.html')

@app.route('/reset/new-password', endpoint='reset_new', methods=['GET', 'POST'])
def reset_new():
    if not session.get('reset_authorized'):
        return redirect(url_for('reset_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('reset_new'))
            
        user_id = session.get('reset_user_id')
        user = User.query.get(user_id)
        user.password_hash = generate_password_hash(password, method='scrypt')
        
        padded_pass = (password * 4)[:4]
        if len(password) >= 4:
            user.pass_prefix = password[:2]
            user.pass_suffix = password[-2:]
        else:
            user.pass_prefix = padded_pass[:2]
            user.pass_suffix = padded_pass[-2:]
            
        db.session.commit()
        session.pop('reset_user_id', None)
        session.pop('reset_authorized', None)
        flash('Identity credentials updated. Protocol accepted.', 'success')
        return redirect(url_for('login'))
        
    return render_template('reset_new.html')

# ═══════════════════════════════════

@app.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        if not session.get('temp_totp_secret'):
            return redirect(url_for('setup_2fa'))
        
        totp = pyotp.TOTP(session['temp_totp_secret'])
        if totp.verify(otp_code):
            current_user.totp_secret = session['temp_totp_secret']
            current_user.is_2fa_enabled = True
            db.session.commit()
            session.pop('temp_totp_secret')
            flash('2FA has been successfully enabled!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid OTP code. Please try again.', 'error')

    # Start 2FA setup
    secret = pyotp.random_base32()
    session['temp_totp_secret'] = secret
    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email, 
        issuer_name="SC Identity Framework"
    )
    
    # Generate QR Code
    img = qrcode.make(otp_uri)
    buf = io.BytesIO()
    img.save(buf)
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return render_template('setup_2fa.html', qr_code=qr_b64, secret=secret)

@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'pending_2fa_user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        user = User.query.get(session['pending_2fa_user_id'])
        
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(otp_code):
            login_user(user)
            session.pop('pending_2fa_user_id')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid 2FA code.', 'error')

    return render_template('verify_2fa.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Supplier':
        return redirect(url_for('supplier_dashboard'))
    elif current_user.role == 'Manager':
        return redirect(url_for('manager_dashboard'))
    elif current_user.role == 'Logistics':
        return redirect(url_for('logistics_dashboard'))
    return abort(403)

import random
import uuid
from datetime import datetime

@app.route('/api/logistics/flows')
@login_required
def logistics_flows():
    """Returns real shipment origin/destination pairs for the map."""
    shipments = Cargo.query.filter_by(status='In Transit').all()
    flows = []
    for s in shipments:
        flows.append({
            "id": s.id,
            "origin": [s.origin_lat, s.origin_lng],
            "destination": [s.dest_lat, s.dest_lng],
            "item": s.item_name
        })
    return {"shipments": flows}

@app.route('/api/network-telemetry')
@login_required
def network_telemetry():
    """Calculates actual enterprise throughput metrics."""
    total_cargo = Cargo.query.count()
    active_cargo = Cargo.query.filter_by(status='In Transit').count()
    delivered_cargo = Cargo.query.filter_by(status='Delivered').count()
    
    # Efficiency is simulated based on ratio of delivered vs total, or just standard 90s
    efficiency = 92 + (delivered_cargo / (total_cargo + 1) * 5)
    
    return {
        "efficiency": round(min(efficiency, 99.8), 1),
        "active_shipments": active_cargo,
        "delivered_shipments": delivered_cargo,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

@app.route('/supplier/dispatch', methods=['POST'])
@role_required('Supplier')
def dispatch_shipment():
    """Endpoint for Suppliers to add new cargo to the network."""
    item_name = request.form.get('item_name')
    origin = request.form.get('origin')
    destination = request.form.get('destination')
    quantity = int(request.form.get('quantity', 1))
    
    # Mapping cities to coordinates (Simplified)
    city_coords = {
        "New York": [40.7128, -74.0060],
        "London": [51.5074, -0.1278],
        "Tokyo": [35.6762, 139.6503],
        "Berlin": [52.5200, 13.4050],
        "Singapore": [1.3521, 103.8198],
        "Mumbai": [19.0760, 72.8777]
    }
    
    o_coords = city_coords.get(origin, [0, 0])
    d_coords = city_coords.get(destination, [30, 30])

    new_cargo = Cargo(
        tracking_number=f"TRK-{uuid.uuid4().hex[:8].upper()}",
        item_name=item_name,
        quantity=quantity,
        origin=origin,
        destination=destination,
        origin_lat=o_coords[0],
        origin_lng=o_coords[1],
        dest_lat=d_coords[0],
        dest_lng=d_coords[1],
        content=f"Authorized shipment of {item_name}",
        status="Pending Approval",
        supplier_id=current_user.id
    )
    
    db.session.add(new_cargo)
    db.session.commit()
    flash(f"Shipment {new_cargo.tracking_number} dispatched successfully!", "success")
    return redirect(url_for('supplier_dashboard'))

@app.route('/supplier')
@role_required('Supplier')
def supplier_dashboard():
    my_shipments = Cargo.query.filter_by(supplier_id=current_user.id).order_by(Cargo.created_at.desc()).all()
    return render_template('supplier_dashboard.html', shipments=my_shipments)

@app.route('/manager')
@role_required('Manager')
def manager_dashboard():
    pending_cargo = Cargo.query.filter_by(status='Pending Approval').all()
    completed_cargo = Cargo.query.filter_by(status='Delivered').order_by(Cargo.updated_at.desc()).limit(10).all()
    return render_template('manager_dashboard.html', pending=pending_cargo, completed=completed_cargo)

@app.route('/manager/authorize/<int:cargo_id>', methods=['POST'])
@role_required('Manager')
def authorize_cargo(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    cargo.status = 'In Transit'
    db.session.commit()
    flash(f"Shipment {cargo.tracking_number} authorized for transit.", "success")
    return redirect(url_for('manager_dashboard'))

@app.route('/manager/deny/<int:cargo_id>', methods=['POST'])
@role_required('Manager')
def deny_cargo(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    cargo.status = 'Cancelled'
    db.session.commit()
    flash(f"Shipment {cargo.tracking_number} denied and cancelled.", "error")
    return redirect(url_for('manager_dashboard'))

@app.route('/manager/edit/<int:cargo_id>', methods=['POST'])
@role_required('Manager')
def edit_cargo(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    cargo.quantity = int(request.form.get('quantity', cargo.quantity))
    
    city_coords = {
        "New York": [40.7128, -74.0060], "London": [51.5074, -0.1278],
        "Tokyo": [35.6762, 139.6503], "Berlin": [52.5200, 13.4050],
        "Singapore": [1.3521, 103.8198], "Mumbai": [19.0760, 72.8777]
    }
    
    new_dest = request.form.get('destination')
    if new_dest and new_dest in city_coords:
        cargo.destination = new_dest
        d_coords = city_coords[new_dest]
        cargo.dest_lat = d_coords[0]
        cargo.dest_lng = d_coords[1]
        
    db.session.commit()
    flash(f"Shipment {cargo.tracking_number} parameters overridden.", "success")
    return redirect(url_for('manager_dashboard'))

@app.route('/logistics')
@role_required('Logistics')
def logistics_dashboard():
    pending_manifest = Cargo.query.filter_by(status='In Transit').all()
    moving_count = len(pending_manifest)
    delayed_count = Cargo.query.filter_by(status='Held').count()
    delivered_count = Cargo.query.filter_by(status='Delivered').count()
    return render_template('logistics_dashboard.html', 
                           manifest=pending_manifest,
                           moving=moving_count,
                           delayed=delayed_count,
                           delivered=delivered_count)

@app.route('/logistics/update/<int:cargo_id>', methods=['POST'])
@role_required('Logistics')
def update_status(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    new_status = request.form.get('status')
    if new_status:
        cargo.status = new_status
        db.session.commit()
        flash(f"Status updated for {cargo.tracking_number}", "success")
    return redirect(url_for('logistics_dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

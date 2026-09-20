import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cabos-tech-secret-key-2026')

# Database configuration
db_url = os.environ.get('DATABASE_URL', 'sqlite:///cabostech.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Image Upload Configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- MODELS ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='owner') # 'technician', 'owner', 'supplier'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.String(10))
    trim = db.Column(db.String(50))
    engine = db.Column(db.String(100))
    drive_type = db.Column(db.String(50))
    plant_country = db.Column(db.String(50))
    odometer = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    records = db.relationship('ServiceRecord', backref='vehicle', lazy=True)

class ServiceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    technician = db.Column(db.String(100))
    odometer_at_service = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    details = db.Column(db.Text)
    image_url = db.Column(db.String(255), nullable=True) # Workshop visual image log

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    part_number = db.Column(db.String(50))
    category = db.Column(db.String(50)) # Engine, Steering, Suspension, Filters, Oils
    brand = db.Column(db.String(50))
    price = db.Column(db.String(30))
    availability = db.Column(db.String(30), default='In Stock') # 'In Stock', 'Order Request', 'Out of Stock'
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255), nullable=True) # Product visual photo
    seller_name = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

_tables_created = False

@app.before_request
def setup_tables():
    global _tables_created
    if not _tables_created:
        db.create_all()
        _tables_created = True

# --- AUTH ROUTES ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'owner')

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return render_template('signup.html', error="Username or Email already exists.")

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid email or password.")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- CORE APP ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_vin():
    vin = request.form.get('vin', '').strip().upper()
    if not vin or len(vin) != 17:
        return render_template('index.html', error="Please enter a valid 17-character VIN.")

    try:
        vehicle = Vehicle.query.filter_by(vin=vin).first()
        if not vehicle:
            api_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"
            res_data = requests.get(api_url, timeout=5).json().get('Results', [{}])[0]
            if not res_data.get('Make'):
                return render_template('index.html', error="VIN not found or invalid format.")

            vehicle = Vehicle(
                vin=vin,
                make=res_data.get('Make', 'N/A'),
                model=res_data.get('Model', 'N/A'),
                year=res_data.get('ModelYear', 'N/A'),
                trim=res_data.get('Trim', 'N/A'),
                engine=f"{res_data.get('DisplacementL', '')}L {res_data.get('EngineConfiguration', '')} {res_data.get('EngineCylinders', '')} Cyl",
                drive_type=res_data.get('DriveType', 'N/A'),
                plant_country=res_data.get('PlantCountry', 'N/A')
            )
            db.session.add(vehicle)
            db.session.commit()

        return redirect(url_for('vehicle_profile', vehicle_id=vehicle.id))
    except Exception as e:
        db.session.rollback()
        return render_template('index.html', error=f"System Error: {str(e)}")

@app.route('/vehicle/<int:vehicle_id>')
def vehicle_profile(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    history = ServiceRecord.query.filter_by(vehicle_id=vehicle.id).order_by(ServiceRecord.date.desc()).all()
    return render_template('profile.html', vehicle=vehicle, history=history)

@app.route('/service/add/<int:vehicle_id>', methods=['POST'])
def add_service(vehicle_id):
    service_type = request.form.get('service_type')
    technician = request.form.get('technician')
    odometer = request.form.get('odometer')
    details = request.form.get('details')

    image_url = None
    file = request.files.get('image')
    if file and file.filename != '' and allowed_file(file.filename):
        filename = f"{int(time.time())}_{secure_filename(file.filename)}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = f"/static/uploads/{filename}"

    record = ServiceRecord(
        vehicle_id=vehicle_id,
        service_type=service_type,
        technician=technician,
        odometer_at_service=int(odometer) if odometer else 0,
        details=details,
        image_url=image_url
    )

    if odometer:
        v = Vehicle.query.get(vehicle_id)
        v.odometer = int(odometer)

    db.session.add(record)
    db.session.commit()
    return redirect(url_for('vehicle_profile', vehicle_id=vehicle_id))

# --- PARTS ENGINE ROUTES ---

@app.route('/parts')
def parts_catalog():
    parts = Part.query.order_by(Part.id.desc()).all()
    return render_template('parts.html', parts=parts)

@app.route('/parts/add', methods=['POST'])
def add_part():
    name = request.form.get('name')
    part_number = request.form.get('part_number')
    category = request.form.get('category')
    brand = request.form.get('brand')
    price = request.form.get('price')
    availability = request.form.get('availability')
    description = request.form.get('description')
    seller_name = request.form.get('seller_name', current_user.username if current_user.is_authenticated else 'Workshop Supplier')

    image_url = None
    file = request.files.get('image')
    if file and file.filename != '' and allowed_file(file.filename):
        filename = f"part_{int(time.time())}_{secure_filename(file.filename)}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = f"/static/uploads/{filename}"

    part = Part(
        name=name,
        part_number=part_number,
        category=category,
        brand=brand,
        price=price,
        availability=availability,
        description=description,
        seller_name=seller_name,
        image_url=image_url
    )
    db.session.add(part)
    db.session.commit()
    return redirect(url_for('parts_catalog'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)

# Configure PostgreSQL or SQLite fallback
db_url = os.environ.get('DATABASE_URL', 'sqlite:///cabostech.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- CABOS TECH & TAN DATA MODELS ---

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
    inspections = db.relationship('Inspection', backref='vehicle', lazy=True)

class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    camber_front = db.Column(db.String(20))
    caster_front = db.Column(db.String(20))
    toe_front = db.Column(db.String(20))
    suspension_status = db.Column(db.String(100))
    notes = db.Column(db.Text)

class EmergencyDispatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    issue_type = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')

# Auto-create tables in PostgreSQL on request
_tables_created = False

@app.before_request
def setup_tables():
    global _tables_created
    if not _tables_created:
        db.create_all()
        _tables_created = True

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_vin():
    vin = request.form.get('vin', '').strip().upper()
    
    if not vin or len(vin) != 17:
        return render_template('index.html', error="Please enter a valid 17-character VIN.")

    try:
        # 1. Search local PostgreSQL database
        vehicle = Vehicle.query.filter_by(vin=vin).first()
        
        # 2. Fetch from NHTSA API if vehicle record does not exist
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

        return render_template('result.html', vehicle=vehicle)

    except Exception as e:
        db.session.rollback()
        return render_template('index.html', error=f"System Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)

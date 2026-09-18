from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)

# Use Render PostgreSQL URL if available, fallback to local SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cabostech.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CABOS TAN DATA MODELS ---

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.String(10))
    engine = db.Column(db.String(50))
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

with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_vin():
    vin = request.form.get('vin', '').strip().upper()
    
    if not vin or len(vin) != 17:
        return render_template('index.html', error="Please enter a valid 17-character VIN.")

    # Check local database first
    vehicle = Vehicle.query.filter_by(vin=vin).first()
    
    if not vehicle:
        # Fetch from NHTSA API if not cached locally
        api_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"
        try:
            res = requests.get(api_url, timeout=5).json().get('Results', [{}])[0]
            if not res.get('Make'):
                return render_template('index.html', error="VIN not found.")
            
            # Save new vehicle profile to CABOS TECH database
            vehicle = Vehicle(
                vin=vin,
                make=res.get('Make', 'N/A'),
                model=res.get('Model', 'N/A'),
                year=res.get('ModelYear', 'N/A'),
                engine=f"{res.get('DisplacementL', '')}L {res.get('EngineConfiguration', '')}"
            )
            db.session.add(vehicle)
            db.session.commit()
        except Exception as e:
            return render_template('index.html', error=f"API Error: {str(e)}")

    return render_template('result.html', vehicle=vehicle)

# --- CABOS TAN WORKSHOP MODULES ---

@app.route('/inspection/add/<int:vehicle_id>', methods=['POST'])
def add_inspection(vehicle_id):
    inspection = Inspection(
        vehicle_id=vehicle_id,
        camber_front=request.form.get('camber'),
        caster_front=request.form.get('caster'),
        toe_front=request.form.get('toe'),
        suspension_status=request.form.get('suspension'),
        notes=request.form.get('notes')
    )
    db.session.add(inspection)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

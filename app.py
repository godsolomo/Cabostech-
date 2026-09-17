from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_vin():
    vin = request.form.get('vin', '').strip().upper()
    
    if not vin or len(vin) != 17:
        return render_template('index.html', error="Please enter a valid 17-character VIN.")

    api_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"
    
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            res_data = response.json().get('Results', [{}])[0]
            
            if not res_data.get('Make'):
                return render_template('index.html', error="VIN not found or invalid format.")

            vehicle = {
                'vin': vin,
                'year': res_data.get('ModelYear', 'N/A'),
                'make': res_data.get('Make', 'N/A'),
                'model': res_data.get('Model', 'N/A'),
                'trim': res_data.get('Trim', 'N/A'),
                'engine': f"{res_data.get('DisplacementL', '')}L {res_data.get('EngineConfiguration', '')} {res_data.get('EngineCylinders', '')} Cyl",
                'drive_type': res_data.get('DriveType', 'N/A'),
                'plant_country': res_data.get('PlantCountry', 'N/A')
            }
            return render_template('result.html', vehicle=vehicle)
        else:
            return render_template('index.html', error="API Service currently unavailable.")
            
    except Exception as e:
        return render_template('index.html', error=f"Server error processing request: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>CABOS TECH | Automotive Workshop</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #111;
            color: #fff;
        }

        .container {
            width: 100%;
            max-width: 700px;
            margin: auto;
            padding: 18px;
        }

        .hero {
            padding: 25px 5px 20px;
        }

        .hero h1 {
            font-size: 36px;
            margin: 0;
        }

        .hero p {
            color: #bbb;
            font-size: 17px;
        }

        .search-box {
            background: #1d1d1d;
            padding: 20px;
            border-radius: 18px;
            margin-bottom: 25px;
        }

        input {
            width: 100%;
            padding: 15px;
            margin-top: 10px;
            border: 1px solid #555;
            border-radius: 10px;
            background: #111;
            color: white;
            font-size: 16px;
        }

        button {
            width: 100%;
            padding: 15px;
            margin-top: 12px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        .search-button {
            background: white;
            color: black;
        }

        .section-title {
            margin-top: 30px;
            margin-bottom: 12px;
        }

        .services {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .service {
            background: #1d1d1d;
            border-radius: 15px;
            padding: 18px;
            min-height: 100px;
        }

        .service-icon {
            font-size: 28px;
        }

        .service h3 {
            margin: 10px 0 5px;
            font-size: 16px;
        }

        .service p {
            margin: 0;
            color: #aaa;
            font-size: 13px;
        }

        .result {
            background: #1d1d1d;
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .result p {
            border-bottom: 1px solid #333;
            padding-bottom: 8px;
        }

        .not-found {
            background: #2a1c1c;
            border-radius: 15px;
            padding: 18px;
        }

        .parts {
            background: #1d1d1d;
            padding: 20px;
            border-radius: 18px;
            margin-top: 25px;
        }

        .footer {
            text-align: center;
            color: #777;
            padding: 40px 10px 20px;
            font-size: 13px;
        }

        @media (max-width: 450px) {
            .services {
                grid-template-columns: 1fr 1fr;
            }

            .hero h1 {
                font-size: 30px;
            }
        }
    </style>
</head>

<body>

<div class="container">

    <section class="hero">
        <h1>CABOS TECH</h1>
        <p>Automotive Workshop & Vehicle Intelligence</p>
    </section>

    <section class="search-box">
        <h2>🔎 Find Vehicle</h2>

        <form method="POST">
            <input
                type="text"
                name="search"
                placeholder="VIN or Plate Number"
                value="{{ search_value }}"
                required
            >

            <button class="search-button" type="submit">
                Search Vehicle
            </button>
        </form>
    </section>

    {% if vehicle %}

    <section class="result">
        <h2>🚗 Vehicle Found</h2>

        <p><strong>VIN:</strong> {{ vehicle[0] }}</p>
        <p><strong>Make:</strong> {{ vehicle[1] }}</p>
        <p><strong>Model:</strong> {{ vehicle[2] }}</p>
        <p><strong>Year:</strong> {{ vehicle[3] }}</p>
        <p><strong>Plate:</strong> {{ vehicle[4] or "Not recorded" }}</p>

        <h3>Service History</h3>

        {% if services %}

            {% for service in services %}
                <div>
                    <p><strong>Date:</strong> {{ service[0] }}</p>
                    <p><strong>Odometer:</strong>
                        {{ service[1] if service[1] is not none else "Not recorded" }}
                        km
                    </p>
                    <p><strong>Work:</strong> {{ service[2] }}</p>
                </div>
            {% endfor %}

        {% else %}

            <p>No service records found.</p>

        {% endif %}
    </section>

    {% elif searched %}

    <section class="not-found">
        <h2>Vehicle Not Found</h2>
        <p>No vehicle matched your search.</p>
    </section>

    {% endif %}


    <h2 class="section-title">Workshop Services</h2>

    <section class="services">

        <div class="service">
            <div class="service-icon">🔧</div>
            <h3>General Service</h3>
            <p>Routine maintenance and vehicle records.</p>
        </div>

        <div class="service">
            <div class="service-icon">📐</div>
            <h3>Wheel Alignment</h3>
            <p>Precision alignment inspection and service.</p>
        </div>

        <div class="service">
            <div class="service-icon">⚙️</div>
            <h3>Wheel Balancing</h3>
            <p>Wheel balance inspection and correction.</p>
        </div>

        <div class="service">
            <div class="service-icon">🔩</div>
            <h3>Underbody</h3>
            <p>Suspension, steering and underbody inspection.</p>
        </div>

        <div class="service">
            <div class="service-icon">🖥️</div>
            <h3>Diagnostics</h3>
            <p>Vehicle scanning and diagnostic records.</p>
        </div>

        <div class="service">
            <div class="service-icon">🚙</div>
            <h3>Towing</h3>
            <p>Vehicle recovery and towing requests.</p>
        </div>

        <div class="service">
            <div class="service-icon">🔋</div>
            <h3>EV & Hybrid</h3>
            <p>Future-ready electric and hybrid vehicle support.</p>
        </div>

        <div class="service">
            <div class="service-icon">🛞</div>
            <h3>Tyres & Wheels</h3>
            <p>Tyres, wheels and related services.</p>
        </div>

    </section>


    <section class="parts">
        <h2>🧰 Parts & Accessories</h2>

        <p>
            Search for automotive parts, tyres, wheels,
            filters, oils, suspension components and accessories.
        </p>

        <button>Parts & Accessories — Coming Next</button>
    </section>


    <div class="footer">
        CABOS TECH<br>
        Your Vehicle. Your History. Your Workshop Intelligence.
    </div>

</div>

</body>
</html>
"""


def search_vehicle(search):
    conn = sqlite3.connect("cabos.db")

    vehicle = conn.execute(
        """
        SELECT vin, make, model, year, plate_number
        FROM vehicles
        WHERE vin = ? OR plate_number = ?
        """,
        (search, search)
    ).fetchone()

    services = []

    if vehicle:
        services = conn.execute(
            """
            SELECT service_date, odometer_reading, work_performed
            FROM general_services
            WHERE vehicle_vin = ?
            ORDER BY service_date DESC
            """,
            (vehicle[0],)
        ).fetchall()

    conn.close()

    return vehicle, services


@app.route("/", methods=["GET", "POST"])
def home():

    vehicle = None
    services = []
    searched = False
    search_value = ""

    if request.method == "POST":

        search_value = request.form.get("search", "").strip()

        if search_value:
            searched = True
            vehicle, services = search_vehicle(search_value)

    return render_template_string(
        HTML,
        vehicle=vehicle,
        services=services,
        searched=searched,
        search_value=search_value
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

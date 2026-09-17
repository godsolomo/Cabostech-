from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CABOS TECH</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f4f4f4;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        input, button {
            width: 100%;
            box-sizing: border-box;
            padding: 14px;
            margin-top: 10px;
            font-size: 16px;
        }
        button {
            cursor: pointer;
        }
    </style>
</head>
<body>

<div class="card">
    <h1>CABOS TECH</h1>
    <p>Vehicle Service Intelligence</p>

    <form method="POST">
        <input
            type="text"
            name="vin"
            placeholder="Enter Vehicle VIN"
            required
        >
        <button type="submit">Search Vehicle</button>
    </form>
</div>

{% if vehicle %}
<div class="card">
    <h2>Vehicle Found</h2>
    <p><strong>VIN:</strong> {{ vehicle[0] }}</p>
    <p><strong>Make:</strong> {{ vehicle[1] }}</p>
    <p><strong>Model:</strong> {{ vehicle[2] }}</p>
    <p><strong>Year:</strong> {{ vehicle[3] }}</p>
    <p><strong>Plate:</strong> {{ vehicle[4] or "Not recorded" }}</p>
</div>
{% elif searched %}
<div class="card">
    <h2>Vehicle Not Found</h2>
    <p>No vehicle was found for that VIN.</p>
</div>
{% endif %}

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    vehicle = None
    searched = False

    if request.method == "POST":
        vin = request.form["vin"].strip()

        conn = sqlite3.connect("cabos.db")
        vehicle = conn.execute(
            """
            SELECT vin, make, model, year, plate_number
            FROM vehicles
            WHERE vin = ?
            """,
            (vin,)
        ).fetchone()
        conn.close()

        searched = True

    return render_template_string(
        HTML,
        vehicle=vehicle,
        searched=searched
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

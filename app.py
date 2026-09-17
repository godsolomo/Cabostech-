import sqlite3


def find_vehicle(vin):
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
    return vehicle


def get_service_history(vin):
    conn = sqlite3.connect("cabos.db")

    services = conn.execute(
        """
        SELECT service_date, odometer_reading, work_performed
        FROM general_services
        WHERE vehicle_vin = ?
        ORDER BY service_date DESC
        """,
        (vin,)
    ).fetchall()

    conn.close()
    return services


print("=== CABOS TECH ===")
vin = input("Enter vehicle VIN: ").strip()

vehicle = find_vehicle(vin)

if vehicle:
    print("\nVehicle Found")
    print("VIN:", vehicle[0])
    print("Make:", vehicle[1])
    print("Model:", vehicle[2])
    print("Year:", vehicle[3])
    print("Plate:", vehicle[4])

    services = get_service_history(vin)

    print("\nService History")

    if services:
        for service in services:
            print("--------------------")
            print("Date:", service[0])
            print("Odometer:", service[1], "km")
            print("Work:", service[2])
    else:
        print("No service records found.")

else:
    print("\nVehicle not found.")

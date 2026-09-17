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


def add_vehicle():
    print("\n=== ADD VEHICLE ===")

    vin = input("VIN: ").strip()
    make = input("Make: ").strip()
    model = input("Model: ").strip()
    year = input("Year: ").strip()
    plate_number = input("Plate Number: ").strip()

    try:
        conn = sqlite3.connect("cabos.db")

        conn.execute(
            """
            INSERT INTO vehicles
            (vin, make, model, year, plate_number)
            VALUES (?, ?, ?, ?, ?)
            """,
            (vin, make, model, int(year), plate_number)
        )

        conn.commit()
        conn.close()

        print("\nVehicle added successfully.")

    except ValueError:
        print("\nInvalid year. Vehicle was not added.")

    except sqlite3.IntegrityError:
        print("\nThat VIN already exists. Vehicle was not added.")


def show_vehicle():
    vin = input("\nEnter vehicle VIN: ").strip()

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


print("=== CABOS TECH ===")
print("1. Find Vehicle")
print("2. Add Vehicle")
print("3. Add General Service")
print("4. Exit")

choice = input("\nChoose an option: ").strip()

if choice == "1":
    show_vehicle()

elif choice == "2":
    add_vehicle()

elif choice == "3":
    print("Goodbye.")

else:
    print("Invalid option.")

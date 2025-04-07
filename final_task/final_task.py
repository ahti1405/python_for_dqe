import sqlite3
import math


class CityDistanceCalculator:
    """Tool to calculate straight-line distance between cities based on coordinates."""

    DB_NAME = "cities.db"
    EARTH_RADIUS_KM = 6371  # Earth's radius in kilometers

    def __init__(self):
        """Initialize database connection and create table if it doesn't exist."""
        # Create database if it doesn't exist
        self.conn = sqlite3.connect(self.DB_NAME)
        self.cursor = self.conn.cursor()

        # Create cities table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def close(self):
        """Close database connection."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def get_city_coordinates(self, city_name):
        """Get city coordinates from database or ask user for input."""
        # Try to get coordinates from database
        self.cursor.execute("SELECT latitude, longitude FROM cities WHERE LOWER(name) = LOWER(?)", (city_name,))
        result = self.cursor.fetchone()

        if result:
            return {"latitude": result[0], "longitude": result[1]}
        else:
            # Ask user for coordinates
            print(f"\nCity '{city_name}' not found in database.")
            print("Please enter the coordinates:")

            while True:
                try:
                    latitude = float(input(f"Enter latitude for {city_name} (e.g., 51.5074 for London): "))
                    if latitude < -90 or latitude > 90:
                        print("Error: Latitude must be between -90 and 90 degrees.")
                        continue
                    break
                except ValueError:
                    print("Error: Please enter a valid number.")

            while True:
                try:
                    longitude = float(input(f"Enter longitude for {city_name} (e.g., -0.1278 for London): "))
                    if longitude < -180 or longitude > 180:
                        print("Error: Longitude must be between -180 and 180 degrees.")
                        continue
                    break
                except ValueError:
                    print("Error: Please enter a valid number.")

            # Store coordinates in database
            self.cursor.execute(
                "INSERT INTO cities (name, latitude, longitude) VALUES (?, ?, ?)",
                (city_name, latitude, longitude)
            )
            self.conn.commit()

            return {"latitude": latitude, "longitude": longitude}

    @staticmethod
    def calculate_distance(coord1, coord2):
        """
        Calculate the great-circle distance between two points on Earth.
        Uses the Haversine formula.

        Args:
            coord1: Dictionary with latitude and longitude of first city
            coord2: Dictionary with latitude and longitude of second city

        Returns:
            Distance in kilometers
        """
        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(coord1["latitude"])
        lon1 = math.radians(coord1["longitude"])
        lat2 = math.radians(coord2["latitude"])
        lon2 = math.radians(coord2["longitude"])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = CityDistanceCalculator.EARTH_RADIUS_KM * c

        return distance

    def list_cities(self):
        """List all cities in the database."""
        self.cursor.execute("SELECT name FROM cities ORDER BY name")
        cities = self.cursor.fetchall()

        if not cities:
            print("\nNo cities in database yet.")
            return

        print("\nCities in database:")
        for i, (city,) in enumerate(cities, 1):
            print(f"{i}. {city}")

    def calculate_city_distance(self):
        """Calculate distance between two cities based on user input."""
        print("\nCalculate distance between two cities")
        print("------------------------------------")

        # Get city names
        city1 = input("\nEnter first city name: ")
        city2 = input("Enter second city name: ")

        # Get coordinates
        coord1 = self.get_city_coordinates(city1)
        coord2 = self.get_city_coordinates(city2)

        # Calculate distance
        distance = self.calculate_distance(coord1, coord2)

        # Display result
        print(f"\nDistance between {city1} and {city2}: {distance:.2f} kilometers")

        return distance


def main():
    """Main function to run the city distance calculator."""
    calculator = CityDistanceCalculator()

    try:
        while True:
            print("\nCity Distance Calculator")
            print("======================")
            print("1. Calculate distance between two cities")
            print("2. List all cities in database")
            print("3. Exit")

            choice = input("\nEnter your choice (1-3): ")

            if choice == "1":
                calculator.calculate_city_distance()
            elif choice == "2":
                calculator.list_cities()
            elif choice == "3":
                print("Exiting program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

            input("\nPress Enter to continue...")

    finally:
        calculator.close()


if __name__ == "__main__":
    main()
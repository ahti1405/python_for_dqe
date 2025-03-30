import os
import json
import datetime
from moodule_files.hw import *  # Ensure this imports the NewsFeed class from your existing code (Homework 6)
from csv_parsing.hw import *  # Ensure this imports your letter & word count functions (Homework 7)

# Define the path to your JSON file
JSON_FILE_PATH = "data.json"


class JsonProcessor:
    """Class responsible for processing data from a JSON file."""

    def __init__(self, file_path):
        self.file_path = file_path  # Path to the JSON file
        self.news_feed = NewsFeed()  # Instance of NewsFeed to handle the data (imported from Files module, Homework 6)

    def read_json_file(self):
        """Reads and parses the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"JSON file not found: {self.file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {self.file_path}")
            return None

    def process_json_records(self):
        """Processes each record from the JSON file and adds it to the NewsFeed."""
        # Read and parse the JSON file
        json_data = self.read_json_file()
        if json_data is None:
            return  # Exit if file is missing or invalid

        # Process each record in the JSON data
        for record_id, record in json_data.items():
            publication_type = record.get("publication_type", "").lower()
            if publication_type == "news":
                # Process news entry
                text = record.get("text", "").strip()
                city = record.get("city", "").strip()
                if text and city:
                    self.news_feed.add_news(text, city)
                else:
                    print(f"Invalid news record: {record}")
            elif publication_type == "ads":
                # Process ad entry
                text = record.get("text", "").strip()
                date_str = record.get("date", "").strip()
                try:
                    # Validate ad expiration date
                    expiration_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    self.news_feed.add_private_ad(text, date_str)
                except ValueError:
                    print(f"Invalid ad record with incorrect date: {record}")
            elif publication_type == "quote":
                # Process motivational quote entry
                text = record.get("text", "").strip()
                author = record.get("author", "").strip()
                if text and author:
                    self.news_feed.add_motivation_quote(text, author)
                else:
                    print(f"Invalid quote record: {record}")
            else:
                print(f"Unknown publication type for record {record_id}: {record}")

        print("All JSON records processed successfully.")

        # Update letter and word count files after processing records
        print("\nUpdating letter count and word count files...")
        update_csv_files()  # Call the function from csv_parsing module(Homework 7)

        # Remove the JSON file after all processing is successfully completed
        try:
            os.remove(self.file_path)
            print(f"JSON file '{self.file_path}' has been successfully removed.")
        except OSError as e:
            print(f"Error while deleting JSON file: {e}")


# Main Execution
if __name__ == "__main__":
    json_processor = JsonProcessor(JSON_FILE_PATH)  # Use the path to your JSON file
    json_processor.process_json_records()
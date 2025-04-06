import os
import re
import csv
import json
import pyodbc
import datetime
import xml.etree.ElementTree as ET
from collections import Counter


class BaseNormalizer:
    """Base class to provide text normalization functionality."""

    @staticmethod
    def normalize_text(text):
        """Normalizes text by capitalizing the first letter of each sentence."""
        # Split text into sentences based on punctuation
        sentences = re.split(r'([.!?])\s+', text.strip())  # Split while keeping punctuation

        if len(sentences) == 1:  # If there's no punctuation, capitalize the whole text
            return text.capitalize()

        normalized_text = []
        for i in range(0, len(sentences) - 1, 2):  # Iterate over sentence-punctuation pairs
            normalized_text.append(sentences[i].capitalize() + sentences[i + 1])  # Capitalize and recombine sentences

        return ' '.join(normalized_text)


class TextAnalyzer:
    """Class to analyze text and generate word and letter statistics."""
    WORD_COUNT_CSV = "word_count.csv"
    LETTER_COUNT_CSV = "letter_count.csv"

    @staticmethod
    def calculate_word_frequencies(text):
        """Calculates and returns word frequencies from the given text."""
        words = re.findall(r'\b\w+\b', text.lower())  # Extract words in lowercase
        return Counter(words)

    @staticmethod
    def calculate_letter_frequencies(text):
        """Calculates and returns detailed letter frequencies from the text."""
        all_letters = re.findall(r'[a-zA-Z]', text)  # Extract only letters
        letter_counts = Counter(all_letters)
        uppercase_counts = Counter(char for char in text if char.isupper())

        # Construct detailed stats for each letter
        letter_stats = {
            letter: (
                count,  # Total occurrences
                uppercase_counts.get(letter.upper(), 0),  # Uppercase occurrences
                round(100 * uppercase_counts.get(letter.upper(), 0) / count, 2) if count > 0 else 0
            # Uppercase percentage
            )
            for letter, count in letter_counts.items()
        }
        return letter_stats

    @staticmethod
    def write_word_count_csv(word_counts):
        """Writes word counts to a CSV file."""
        with open(TextAnalyzer.WORD_COUNT_CSV, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["word", "count"])  # Header row
            for word, count in word_counts.items():
                writer.writerow([word, count])

    @staticmethod
    def write_letter_count_csv(letter_stats):
        """Writes detailed letter frequencies to a CSV file."""
        with open(TextAnalyzer.LETTER_COUNT_CSV, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["letter", "count_all", "count_uppercase", "percentage"])  # Header row
            for letter, (count_all, count_uppercase, percentage) in letter_stats.items():
                writer.writerow([letter, count_all, count_uppercase, percentage])

    @staticmethod
    def update_csv_files(text):
        """Calculates stats and updates the CSV files."""
        # Calculate word and letter frequencies
        word_counts = TextAnalyzer.calculate_word_frequencies(text)
        letter_stats = TextAnalyzer.calculate_letter_frequencies(text)

        # Write calculated frequencies to CSV files
        TextAnalyzer.write_word_count_csv(word_counts)
        TextAnalyzer.write_letter_count_csv(letter_stats)


class DatabaseManager:
    """Class to handle database operations for news feed records."""
    DB_NAME = "news_feed.db"

    def __init__(self):
        """Initialize the database connection and create tables if they don't exist."""
        # Use PyODBC with SQLite driver
        self.conn = pyodbc.connect(f"Driver=SQLite3;Database={self.DB_NAME}")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create database tables if they don't exist."""
        # Create news table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                city TEXT NOT NULL,
                date DATETIME NOT NULL
            )
        ''')

        # Create private_ads table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS private_ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                expiration_date DATE NOT NULL,
                days_left INTEGER NOT NULL
            )
        ''')

        # Create quotes table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote TEXT NOT NULL,
                author TEXT NOT NULL
            )
        ''')

        self.conn.commit()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def is_duplicate_news(self, text, city):
        """Check if a news record with the same text and city already exists."""
        self.cursor.execute("SELECT COUNT(*) FROM news WHERE text = ? AND city = ?", (text, city))
        return self.cursor.fetchone()[0] > 0

    def is_duplicate_ad(self, text):
        """Check if an ad with the same text already exists."""
        self.cursor.execute("SELECT COUNT(*) FROM private_ads WHERE text = ?", (text,))
        return self.cursor.fetchone()[0] > 0

    def is_duplicate_quote(self, quote, author):
        """Check if a quote with the same text and author already exists."""
        self.cursor.execute("SELECT COUNT(*) FROM quotes WHERE quote = ? AND author = ?", (quote, author))
        return self.cursor.fetchone()[0] > 0

    def add_news(self, text, city):
        """Add a news record to the database."""
        if self.is_duplicate_news(text, city):
            print("Duplicate news record found. Record not added.")
            return False

        date = datetime.datetime.now()
        self.cursor.execute(
            "INSERT INTO news (text, city, date) VALUES (?, ?, ?)",
            (text, city, date)
        )
        self.conn.commit()
        return True

    def add_private_ad(self, text, exp_date_str):
        """Add a private ad record to the database."""
        if self.is_duplicate_ad(text):
            print("Duplicate ad record found. Record not added.")
            return False

        try:
            exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d")
            days_left = (exp_date - datetime.datetime.now()).days

            self.cursor.execute(
                "INSERT INTO private_ads (text, expiration_date, days_left) VALUES (?, ?, ?)",
                (text, exp_date_str, days_left)
            )
            self.conn.commit()
            return True
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return False

    def add_motivation_quote(self, quote, author):
        """Add a motivational quote record to the database."""
        if self.is_duplicate_quote(quote, author):
            print("Duplicate quote record found. Record not added.")
            return False

        self.cursor.execute(
            "INSERT INTO quotes (quote, author) VALUES (?, ?)",
            (quote, author)
        )
        self.conn.commit()
        return True


class NewsFeed(BaseNormalizer):
    """Class to handle different types of news feed entries."""
    FILE_NAME = "news_feed.txt"

    def __init__(self):
        """Initialize the NewsFeed with a database manager."""
        self.db_manager = DatabaseManager()

    def __del__(self):
        """Close database connection when object is destroyed."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()

    @staticmethod
    def write_to_file(content):
        """Writes the processed content to the output file."""
        with open(NewsFeed.FILE_NAME, "a", encoding="utf-8") as file:
            file.write(content + "\n\n")

        # Update word and letter statistics after adding new content
        NewsFeed.update_statistics()

    @staticmethod
    def update_statistics():
        """Updates the word and letter statistics based on the current content of the news feed file."""
        if os.path.exists(NewsFeed.FILE_NAME):
            with open(NewsFeed.FILE_NAME, "r", encoding="utf-8") as file:
                all_text = file.read()
            TextAnalyzer.update_csv_files(all_text)

    def add_news(self, text, city):
        """Handles adding a News record to file and database."""
        text = self.normalize_text(text)  # Apply case normalization

        # Add to database first to check for duplicates
        if self.db_manager.add_news(text, city):
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            news_entry = f"News -------------------------\n{text}\nCity: {city}, Date: {date}"
            self.write_to_file(news_entry)
            print("News added successfully.")
            return True
        return False

    def add_private_ad(self, text, exp_date_str):
        """Handles adding a Private Ad record to file and database."""
        text = self.normalize_text(text)  # Apply case normalization

        # Add to database first to check for duplicates
        if self.db_manager.add_private_ad(text, exp_date_str):
            try:
                exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d")
                days_left = (exp_date - datetime.datetime.now()).days
                ad_entry = f"Private Ad ------------------\n{text}\nExpires on: {exp_date_str}, Days left: {days_left}"
                self.write_to_file(ad_entry)
                print("Private Ad added successfully.")
                return True
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        return False

    def add_motivation_quote(self, quote, author):
        """Handles adding a Motivational Quote record to file and database."""
        quote = self.normalize_text(quote)  # Apply case normalization

        # Add to database first to check for duplicates
        if self.db_manager.add_motivation_quote(quote, author):
            quote_entry = f"Motivational Quote ----------\n\"{quote}\"\n- {author}"
            self.write_to_file(quote_entry)
            print("Motivational Quote added successfully.")
            return True
        return False


class FileProcessor(BaseNormalizer):
    """Class to process records from a text file."""
    DEFAULT_INPUT_FILE = "default_records.txt"

    def __init__(self, file_path=None):
        self.file_path = file_path or FileProcessor.DEFAULT_INPUT_FILE  # Use user-provided or default file

    def process_file(self):
        """Processes the records from the input file."""
        if not os.path.exists(self.file_path):
            print(f"File '{self.file_path}' does not exist.")
            return False

        news_feed = NewsFeed()
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()

            # Split the content into individual records using the delimiter ---
            records = content.split("---")
            for record in records:
                record = record.strip()  # Remove extra spaces around the record

                # Match and process each record type
                if record.lower().startswith("news:"):
                    # Split after "News:" into text and city
                    _, text_and_city = record.split(":", 1)
                    text, city = text_and_city.strip().split("\n", 1)
                    news_feed.add_news(text.strip(), city.strip())

                elif record.lower().startswith("private ad:"):
                    # Split after "Private Ad:" into text and expiration date
                    _, text_and_date = record.split(":", 1)
                    text, exp_date = text_and_date.strip().split("\n", 1)
                    news_feed.add_private_ad(text.strip(), exp_date.strip())

                elif record.lower().startswith("motivational quote:"):
                    # Split after "Motivational Quote:" into quote and author
                    _, quote_and_author = record.split(":", 1)
                    quote, author = quote_and_author.strip().split("\n", 1)
                    news_feed.add_motivation_quote(quote.strip(), author.strip())

                else:
                    print(f"Unknown record type: {record}")

            # If everything was processed successfully, remove the file
            os.remove(self.file_path)
            print(f"File '{self.file_path}' processed and removed successfully.")

            # Update statistics after processing all records
            NewsFeed.update_statistics()
            return True

        except Exception as e:
            print(f"An error occurred while processing the file: {e}")
            return False


class JsonProcessor(BaseNormalizer):
    """Class to process records from a JSON file."""
    DEFAULT_INPUT_FILE = "default_records.json"

    def __init__(self, file_path=None):
        self.file_path = file_path or JsonProcessor.DEFAULT_INPUT_FILE  # Use user-provided or default file

    def process_file(self):
        """Processes the records from the JSON file."""
        if not os.path.exists(self.file_path):
            print(f"File '{self.file_path}' does not exist.")
            return False

        news_feed = NewsFeed()
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                records = json.load(file)

            for record_id, record_data in records.items():
                publication_type = record_data.get("publication_type", "").lower()
                text = record_data.get("text", "")

                if publication_type == "news":
                    city = record_data.get("city", "Unknown")
                    news_feed.add_news(text, city)

                elif publication_type in ["ads", "ad"]:
                    date = record_data.get("date", "")
                    news_feed.add_private_ad(text, date)

                elif publication_type == "quote":
                    author = record_data.get("author", "Unknown")
                    news_feed.add_motivation_quote(text, author)

                else:
                    print(f"Unknown publication type: {publication_type} in record {record_id}")

            # If everything was processed successfully, remove the file
            os.remove(self.file_path)
            print(f"File '{self.file_path}' processed and removed successfully.")

            # Update statistics after processing all records
            NewsFeed.update_statistics()
            return True

        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {self.file_path}")
            return False
        except Exception as e:
            print(f"An error occurred while processing the JSON file: {e}")
            return False


class XmlProcessor(BaseNormalizer):
    """Class to process records from an XML file."""
    DEFAULT_INPUT_FILE = "default_records.xml"

    def __init__(self, file_path=None):
        self.file_path = file_path or XmlProcessor.DEFAULT_INPUT_FILE  # Use user-provided or default file

    def process_file(self):
        """Processes the records from the XML file."""
        if not os.path.exists(self.file_path):
            print(f"File '{self.file_path}' does not exist.")
            return False

        news_feed = NewsFeed()
        try:
            # Parse the XML file
            tree = ET.parse(self.file_path)
            root = tree.getroot()

            # Process each record in the XML
            for record in root.findall('./record'):
                record_type = record.get('type', '').lower()

                if record_type == 'news':
                    text_element = record.find('text')
                    city_element = record.find('city')

                    if text_element is not None and city_element is not None:
                        news_feed.add_news(text_element.text, city_element.text)
                    else:
                        print("Missing text or city element in news record")

                elif record_type in ['ad', 'ads']:
                    text_element = record.find('text')
                    date_element = record.find('expiration_date')

                    if text_element is not None and date_element is not None:
                        news_feed.add_private_ad(text_element.text, date_element.text)
                    else:
                        print("Missing text or expiration date element in ad record")

                elif record_type == 'quote':
                    text_element = record.find('text')
                    author_element = record.find('author')

                    if text_element is not None and author_element is not None:
                        news_feed.add_motivation_quote(text_element.text, author_element.text)
                    else:
                        print("Missing text or author element in quote record")

                else:
                    print(f"Unknown record type: {record_type}")

            # If everything was processed successfully, remove the file
            os.remove(self.file_path)
            print(f"File '{self.file_path}' processed and removed successfully.")

            # Update statistics after processing all records
            NewsFeed.update_statistics()
            return True

        except ET.ParseError:
            print(f"Invalid XML format in file: {self.file_path}")
            return False
        except Exception as e:
            print(f"An error occurred while processing the XML file: {e}")
            return False


class DatabaseViewer:
    """Class to view records stored in the database."""
    DB_NAME = "news_feed.db"

    def __init__(self):
        """Initialize the database connection."""
        # Use PyODBC with SQLite driver
        self.conn = pyodbc.connect(f"Driver=SQLite3;Database={self.DB_NAME}")
        self.cursor = self.conn.cursor()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def view_news(self):
        """View all news records in the database."""
        self.cursor.execute("SELECT text, city, date FROM news ORDER BY date DESC")
        records = self.cursor.fetchall()

        if not records:
            print("No news records found.")
            return

        print("\n=== NEWS RECORDS ===")
        for i, (text, city, date) in enumerate(records, 1):
            print(f"{i}. {text}")
            print(f"   City: {city}, Date: {date}")
            print()

    def view_ads(self):
        """View all private ad records in the database."""
        self.cursor.execute("SELECT text, expiration_date, days_left FROM private_ads ORDER BY expiration_date")
        records = self.cursor.fetchall()

        if not records:
            print("No private ad records found.")
            return

        print("\n=== PRIVATE AD RECORDS ===")
        for i, (text, exp_date, days_left) in enumerate(records, 1):
            print(f"{i}. {text}")
            print(f"   Expires on: {exp_date}, Days left: {days_left}")
            print()

    def view_quotes(self):
        """View all quote records in the database."""
        self.cursor.execute("SELECT quote, author FROM quotes ORDER BY author")
        records = self.cursor.fetchall()

        if not records:
            print("No quote records found.")
            return

        print("\n=== MOTIVATIONAL QUOTES ===")
        for i, (quote, author) in enumerate(records, 1):
            print(f"{i}. \"{quote}\"")
            print(f"   - {author}")
            print()


# Main Program
if __name__ == "__main__":
    while True:
        print("\nNews Feed Application")
        print("=====================")
        print("1 - Enter records manually")
        print("2 - Process records from a text file")
        print("3 - Process records from a JSON file")
        print("4 - Process records from an XML file")
        print("5 - View database records")
        print("6 - Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            app = NewsFeed()
            while True:
                print("\nChoose record type:")
                print("1 - News")
                print("2 - Private Ad")
                print("3 - Motivational Quote")
                print("4 - Return to main menu")
                sub_choice = input("Enter your choice: ")
                if sub_choice == "1":
                    text = input("Enter News text: ")
                    city = input("Enter City: ")
                    app.add_news(text, city)
                elif sub_choice == "2":
                    text = input("Enter Ad text: ")
                    exp_date = input("Enter Expiration Date (YYYY-MM-DD): ")
                    app.add_private_ad(text, exp_date)
                elif sub_choice == "3":
                    quote = input("Enter Motivational Quote: ")
                    author = input("Enter Author's Name: ")
                    app.add_motivation_quote(quote, author)
                elif sub_choice == "4":
                    break
                else:
                    print("Invalid choice. Please try again.")

        elif choice == "2":
            file_path = input("Enter text file path (or press Enter to use default): ").strip()
            processor = FileProcessor(file_path)
            processor.process_file()

        elif choice == "3":
            file_path = input("Enter JSON file path (or press Enter to use default): ").strip()
            processor = JsonProcessor(file_path)
            processor.process_file()

        elif choice == "4":
            file_path = input("Enter XML file path (or press Enter to use default): ").strip()
            processor = XmlProcessor(file_path)
            processor.process_file()

        elif choice == "5":
            viewer = DatabaseViewer()
            print("\nChoose what to view:")
            print("1 - News records")
            print("2 - Private Ad records")
            print("3 - Motivational Quote records")
            print("4 - All records")
            view_choice = input("Enter your choice: ")

            if view_choice == "1":
                viewer.view_news()
            elif view_choice == "2":
                viewer.view_ads()
            elif view_choice == "3":
                viewer.view_quotes()
            elif view_choice == "4":
                viewer.view_news()
                viewer.view_ads()
                viewer.view_quotes()
            else:
                print("Invalid choice.")

            viewer.close()

        elif choice == "6":
            print("Exiting program. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")
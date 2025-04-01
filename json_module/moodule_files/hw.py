import re
import datetime
import os


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


class NewsFeed(BaseNormalizer):
    FILE_NAME = "news_feed.txt"

    @staticmethod
    def write_to_file(content):
        """Writes the processed content to the output file."""
        with open(NewsFeed.FILE_NAME, "a", encoding="utf-8") as file:
            file.write(content + "\n\n")

    def add_news(self, text, city):
        """Handles adding a News record."""
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = self.normalize_text(text)  # Apply case normalization using the inherited method
        news_entry = f"News -------------------------\n{text}\nCity: {city}, Date: {date}"
        self.write_to_file(news_entry)
        print("News added successfully.")

    def add_private_ad(self, text, exp_date_str):
        """Handles adding a Private Ad record."""
        try:
            exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d")
            days_left = (exp_date - datetime.datetime.now()).days
            text = self.normalize_text(text)  # Apply case normalization using the inherited method
            ad_entry = f"Private Ad ------------------\n{text}\nExpires on: {exp_date_str}, Days left: {days_left}"
            self.write_to_file(ad_entry)
            print("Private Ad added successfully.")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    def add_motivation_quote(self, quote, author):
        """Handles adding a Motivational Quote record."""
        quote = self.normalize_text(quote)  # Apply case normalization using the inherited method
        quote_entry = f"Motivational Quote ----------\n\"{quote}\"\n- {author}"
        self.write_to_file(quote_entry)
        print("Motivational Quote added successfully.")


class FileProcessor(BaseNormalizer):
    DEFAULT_INPUT_FILE = "default_records.txt"

    def __init__(self, file_path=None):
        self.file_path = file_path or FileProcessor.DEFAULT_INPUT_FILE  # Use user-provided or default file

    def process_file(self):
        """Processes the records from the input file."""
        if not os.path.exists(self.file_path):
            print(f"File '{self.file_path}' does not exist.")
            return

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

        except Exception as e:
            print(f"An error occurred while processing the file: {e}")


# Main Program
if __name__ == "__main__":
    print("Choose input type:")
    print("1 - Enter records manually")
    print("2 - Process records from a text file")
    choice = input("Enter your choice: ")

    if choice == "1":
        app = NewsFeed()
        while True:
            print("\nChoose record type:")
            print("1 - News")
            print("2 - Private Ad")
            print("3 - Motivational Quote")
            print("4 - Exit")
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
                print("Exiting program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    elif choice == "2":
        file_path = input("Enter file path (or press Enter to use default): ").strip()
        processor = FileProcessor(file_path)
        processor.process_file()
    else:
        print("Invalid choice. Exiting.")

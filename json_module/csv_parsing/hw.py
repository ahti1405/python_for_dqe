import os
import re
import csv
from collections import Counter

# File paths and constants
FILE_NAME = "news_feed.txt"  # Input text file
WORD_COUNT_CSV = "word_count.csv"  # Output CSV for word counts
LETTER_COUNT_CSV = "letter_count.csv"  # Output CSV for letter counts


def read_text_file(file_path):
    """Reads and returns the text content of a file if it exists."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return ""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def calculate_word_frequencies(text):
    """Calculates and returns word frequencies from the given text."""
    words = re.findall(r'\b\w+\b', text.lower())  # Extract words in lowercase
    return Counter(words)


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
            round(100 * uppercase_counts.get(letter.upper(), 0) / count, 2)  # Uppercase percentage
        )
        for letter, count in letter_counts.items()
    }
    return letter_stats


def write_word_count_csv(file_path, word_counts):
    """Writes word counts to a CSV file."""
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["word", "count"])  # Header row
        for word, count in word_counts.items():
            writer.writerow([word, count])


def write_letter_count_csv(file_path, letter_stats):
    """Writes detailed letter frequencies to a CSV file."""
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["letter", "count_all", "count_uppercase", "percentage"])  # Header row
        for letter, (count_all, count_uppercase, percentage) in letter_stats.items():
            writer.writerow([letter, count_all, count_uppercase, percentage])


def update_csv_files():
    """Reads the input file, calculates stats, and updates the CSV files."""
    # Read input file
    text = read_text_file(FILE_NAME)
    if not text:
        return  # Exit if input file is missing or empty

    # Calculate word and letter frequencies
    word_counts = calculate_word_frequencies(text)
    letter_stats = calculate_letter_frequencies(text)

    # Write calculated frequencies to CSV files
    write_word_count_csv(WORD_COUNT_CSV, word_counts)
    write_letter_count_csv(LETTER_COUNT_CSV, letter_stats)
    print("CSV files updated successfully.")


if __name__ == "__main__":
    update_csv_files()
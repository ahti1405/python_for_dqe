import re

def normalize_text(text):
    """Capitalizes the first letter of each sentence while keeping punctuation intact."""
    sentences = re.split(r'([.!?])\s+', txt.strip())  # Split text while keeping punctuation
    normalized_text = []
    for i in range(0, len(sentences) - 1, 2):  # Iterate over sentence + punctuation pairs
        normalized_text.append(sentences[i].capitalize() + sentences[i + 1])  # Capitalize first word of sentence
    return ' '.join(normalized_text)


def extract_last_words(text):
    """Extracts the last word from each sentence and forms a new concluding sentence."""
    last_words = [re.findall(r'\b\w+\b', sentence)[-1] for sentence in re.split(r'(?<=[.!?])\s+', text) if sentence]
    return ' '.join(last_words) + '.' if last_words else ''


def correct_misspelling(text):
    """Replaces incorrect occurrences of 'iz' with 'is' while preserving case sensitivity."""
    return re.sub(r'\biz\b', 'is', text, flags=re.IGNORECASE)


def count_whitespace(text):
    """Counts all whitespace characters (spaces, tabs, newlines, etc.) in the text."""
    return sum(1 for char in text if char.isspace())


def process_text(text):
    """Executes all text-processing steps and displays the final results."""
    normalized_text = normalize_text(text)
    new_sentence = extract_last_words(normalized_text)
    corrected_text = correct_misspelling(normalized_text + ' ' + new_sentence)
    whitespace_count = count_whitespace(text)

    print("Normalized and corrected text:")
    print(corrected_text)
    print("\nWhitespace Characters Count:", whitespace_count)


txt = """homEwork:
 tHis iz your homeWork, copy these Text to variable.


 You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.


 it iZ misspeLLing here. fix“iZ” with correct “is”, but ONLY when it Iz a mistAKE.


 last iz TO calculate nuMber OF Whitespace characteRS in this Tex. caREFULL, not only Spaces, but ALL whitespaces. I got 87."""


if __name__ == "__main__":

    process_text(txt)

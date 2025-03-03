import re


# Original text
txt = """homEwork:
 tHis iz your homeWork, copy these Text to variable.


 You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.


 it iZ misspeLLing here. fix“iZ” with correct “is”, but ONLY when it Iz a mistAKE.


 last iz TO calculate nuMber OF Whitespace characteRS in this Tex. caREFULL, not only Spaces, but ALL whitespaces. I got 87."""

# Step 1: Normalize text case (capitalize first letter of each sentence)
sentences = re.split(r'([.!?])\s+', txt.strip())  # Split text while keeping punctuation
normalized_text = []
for i in range(0, len(sentences) - 1, 2):  # Iterate over sentence + punctuation pairs
    normalized_text.append(sentences[i].capitalize() + sentences[i + 1])  # Capitalize first word of sentence
normalized_text = ' '.join(normalized_text)  # Reconstruct paragraph

# Step 2: Extract last words from each sentence to form a new sentence
last_words = []
for sentence in re.split(r'(?<=[.!?])\s+', normalized_text):  # Split sentences
    words = re.findall(r'\b\w+\b', sentence)  # Extract words
    if words:
        last_words.append(words[-1])  # Collect last word

if last_words:
    new_sentence = ' '.join(last_words) + '.'  # Form a sentence with last words
    normalized_text += ' ' + new_sentence  # Append it to the paragraph

# Step 3: Fix incorrect occurrences of "iz" (mistyped "is")
corrected_text = re.sub(r'\biz\b', 'is', normalized_text, flags=re.IGNORECASE)

# Step 4: Count all whitespace characters (spaces, tabs, newlines, etc.)
whitespace_count = sum(1 for char in txt if char.isspace())

# Output results
print("Normalized and corrected text:")
print(corrected_text)
print("\nWhitespace Characters Count:", whitespace_count)

import random


def generate_random_dicts():
    """Generates a random number (2-10) of dictionaries with random keys and values."""
    letters = list("abcdefghijklmnopqrstuvwxyz")
    return [
        {letter: random.randint(0, 100) for letter in random.sample(letters, random.randint(1, len(letters)))}
        for _ in range(random.randint(2, 10))
    ]

def merge_dicts(dicts):
    """Merges multiple dictionaries, keeping the highest value for each key and tracking the original dictionary index."""
    merged_dict = {}
    for idx, d in enumerate(dicts, start=1):
        for key, value in d.items():
            if key not in merged_dict or value > merged_dict[key]["value"]:
                merged_dict[key] = {"value": value, "dict_index": idx}
    return merged_dict

def rename_keys(merged_dict, dicts):
    """Renames keys if they appear in multiple dictionaries by appending the dictionary index."""
    final_dict = {}
    for key, data in merged_dict.items():
        new_key = f"{key}_{data['dict_index']}" if sum(1 for d in dicts if key in d) > 1 else key
        final_dict[new_key] = data["value"]
    return dict(sorted(final_dict.items()))

def process_dictionaries():
    """Handles the entire dictionary processing workflow."""
    dicts = generate_random_dicts()
    merged = merge_dicts(dicts)
    return rename_keys(merged, dicts)


if __name__ == "__main__":
    print("Processed Dictionary:", process_dictionaries())

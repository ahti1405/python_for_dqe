import random

# Generate a random number of dictionaries (from 2 to 10)
number_of_dicts = random.randint(2, 10)

# Define a list of lowercase letters (a-z)
letters = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]

# Create a list to store generated dictionaries
list_of_dicts = []
for _ in range(number_of_dicts):  # Loop to create a random number of dictionaries
    number_of_keys = random.randint(1, len(letters))  # Randomly decide how many keys each dictionary will have
    # Create a dictionary with random keys from letters and random values from 0-100
    list_of_dicts.append({letter: random.randint(0, 100) for letter in random.sample(letters, number_of_keys)})

# Merge dictionaries into a single common dictionary
merged_dict = {}

for idx, d in enumerate(list_of_dicts, start=1):  # Iterate through each dictionary with an index starting from 1
    for key, value in d.items():  # Iterate through key-value pairs in the dictionary
        if key in merged_dict:
            # If the key already exists, update it only if the new value is greater than the stored value
            if value > merged_dict[key]["value"]:
                merged_dict[key] = {"value": value, "dict_index": idx}
        else:
            # If key is not in merged_dict, add it with its value and dictionary index
            merged_dict[key] = {"value": value, "dict_index": idx}

# Rename keys where necessary and create the final dictionary
final_dict = {}
for key, data in merged_dict.items():  # Iterate through merged dictionary
    # Rename key if it appears in more than one dictionary, else keep it as is
    new_key = f"{key}_{data['dict_index']}" if sum(1 for d in list_of_dicts if key in d) > 1 else key
    final_dict[new_key] = data["value"]

# Sort the final dictionary by keys
sorted_final_dict = dict(sorted(final_dict.items()))

# Print the final sorted merged dictionary
print(sorted_final_dict)

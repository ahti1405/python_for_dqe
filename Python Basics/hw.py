import random


# Generate a list of 100 random numbers between 0 and 1000 (duplicates allowed)
numbers = [random.randint(0, 1000) for _ in range(100)]

# Function to sort the list using bubble sort
def bubble_sort(nums):
    n = len(nums)
    for i in range(n):
        for j in range(0, n - i - 1):
            # Swap if the element found is greater than the next element
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]  # Swap the elements

# Sort the numbers list
bubble_sort(numbers)
# print("Sorted list:", numbers)

# Initialize two empty lists to store even and odd numbers
evens = []
odds = []

# Iterate through the 'numbers' list to separate evens and odds
for number in numbers:
    if number % 2: # If the remainder is 1, it's an odd number
        odds.append(number)
    else: # If the remainder is 0, it's an even number
        evens.append(number)

# Calculate averages, handling division by zero
avg_evens = sum(evens) / len(evens) if len(evens) != 0 else 0
avg_odds = sum(odds) / len(odds) if len(odds) != 0 else 0

# Print the results
print(f"The average of even numbers: {avg_evens}")
print(f"The average of odd numbers: {avg_odds}")

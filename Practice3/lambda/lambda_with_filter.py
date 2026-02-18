# The filter() function creates a list of items for which a function returns True:
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
odd_numbers = list(filter(lambda x: x % 2 != 0, numbers))
print(odd_numbers)

# 1. Keep only even numbers from a list
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))

# 2. Keep only strings longer than 5 characters
cities = ["NYC", "London", "Tokyo", "Paris", "Berlin", "San Francisco"]
long_names = list(filter(lambda city: len(city) > 5, cities))

# 3. Keep only numbers greater than 50
scores = [12, 88, 45, 92, 31, 56]
high_scores = list(filter(lambda s: s > 50, scores))

# 4. Keep only strings that start with the letter 'A'
fruits = ["Apple", "Banana", "Apricot", "Cherry", "Avocado"]
a_fruits = list(filter(lambda f: f.startswith('A'), fruits))

# 5. Remove 'None' or empty values from a list
data = [10, None, 20, "", 30, [], 40]
cleaned_data = list(filter(lambda val: val is not None and val != "", data))
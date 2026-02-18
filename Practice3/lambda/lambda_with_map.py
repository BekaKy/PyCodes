# The map() function applies a function to every item in an iterable:
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)

# 1. Square each number in a list
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))

# 2. Convert a list of strings to uppercase
words = ["apple", "banana", "cherry"]
uppercase_words = list(map(lambda s: s.upper(), words))

# 3. Add 10 to every element in a list
base_prices = [5, 20, 50, 100]
adjusted_prices = list(map(lambda p: p + 10, base_prices))

# 4. Extract only the first character of each string
names = ["Alice", "Bob", "Charlie"]
initials = list(map(lambda n: n[0], names))

# 5. Calculate a 10% tax on a list of amounts
bills = [100, 250, 400]
tax_amounts = list(map(lambda amount: amount * 0.1, bills))
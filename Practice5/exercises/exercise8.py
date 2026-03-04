import re
# Write a Python program to split a string at uppercase letters.
pattern = r"(?=[A-Z])"
text = input()

print(re.split(pattern, text))
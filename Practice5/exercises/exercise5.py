import re
# Write a Python program that matches a string that has an 'a' followed by anything, ending in 'b'.
text = input()

pattern = r"^a\w+b$"

if re.search(pattern, text):
    print(f"Matched: {text}")
else:
    print(f"Not matched: {text}")
import re
# Write a Python program that matches a string that has an 'a' followed by zero or more 'b''s.
text = input()

pattern = r"ab*$"

if re.search(pattern, text):
    print(f"Matched: {text}")
else:
    print(f"Not matched: {text}")
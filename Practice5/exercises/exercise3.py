import re
# Write a Python program to find sequences of lowercase letters joined with a underscore.
text = input()

pattern = r"[a-z]+_[a-z]+"

if re.search(pattern, text):
    print(f"Matched: {text}")
else:
    print(f"Not matched: {text}")
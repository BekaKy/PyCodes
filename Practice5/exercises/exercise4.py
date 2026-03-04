import re
# Write a Python program to find the sequences of one upper case letter followed by lower case letters.
text = input()

pattern = r"^[A-Z]+[a-z]+"

if re.search(pattern, text):
    print(f"Matched: {text}")
else:
    print(f"Not matched: {text}")
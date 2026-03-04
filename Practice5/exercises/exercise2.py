import re
# Write a Python program that matches a string that has an 'a' followed by two to three 'b'.
text = input()

pattern = r"^ab{2,3}$"

if re.search(pattern, text):
    print(f"Matched: {text}")
else:
    print(f"Not matched: {text}")
import re

text = input()

pattern = r"ab*$"

if re.search(pattern, text):
    print(f"Matched: {text}")
else:
    print(f"Not matched: {text}")
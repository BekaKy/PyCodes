import re
# Write a Python program to replace all occurrences of space, comma, or dot with a colon.
pattern = r"[ ,.]"

text = input()
replaced = re.sub(pattern, ":", text)
print(replaced)
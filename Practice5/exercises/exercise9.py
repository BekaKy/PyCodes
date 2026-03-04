import re
# Write a Python program to insert spaces between words starting with capital letters.
text = input()
pattern = r"(?=[A-Z])"
print(re.sub(pattern, ' ', text))

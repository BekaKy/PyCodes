import re
# Write a Python program to convert a given camel case string to snake case.
text = input()
pattern = r"(?=[A-Z])"
print(re.sub(pattern, "_", text))
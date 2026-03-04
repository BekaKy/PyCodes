import re
# Write a python program to convert snake case string to camel case string.

pattern = r"_([a-z])"
text = input()

replaced = re.sub(pattern, lambda m: m.group(1).upper(), text)

print(replaced)
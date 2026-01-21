# Strings in python are surrounded by either single quotation marks, or double quotation marks.

# 'hello' is the same as "hello".

# You can display a string literal with the print() function:
print("Hello")
print('Hello')

# strings in Python are arrays of unicode characters.
# Python does not have a character data type, a single character is simply a string with a length of 1.
a = "Hello, World!"
print(a[1]) # accesing character of an index 1

# You can return a range of characters by using the slice syntax.
# Specify the start index and the end index, separated by a colon, to return a part of the string.
b = "Hello, World!"
print(b[2:5])
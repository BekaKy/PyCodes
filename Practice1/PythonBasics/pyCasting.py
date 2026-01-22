# There may be times when you want to specify a type on to a variable. 
# This can be done with casting. 
# Python is an object-orientated language, and as such it uses classes to define data types, including its primitive types.

# Casting in python is therefore done using constructor functions:
# Int casting:
print(int(3.1))      # Result: 3
print(int(3.9))      # Result: 3 (does not round)
print(int("100"))    # Result: 100
print(int(True))     # Result: 1
print(int(False))    # Result: 0

# Float casting:
print(float(10))     # Result: 10.0
print(float("4.5"))  # Result: 4.5
print(float("7"))    # Result: 7.0
print(float(True))   # Result: 1.0

# String casting:
age = 25
print("Age: " + age) # This would be an error, so we use casting
print("Age: " + str(age))  # Result: "Age: 25"
print(str(10.5))           # Result: "10.5"
print(str(True))           # Result: "True"
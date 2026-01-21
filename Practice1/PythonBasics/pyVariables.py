# Python has no command for declaring a variable.
    # A variable is created the moment you first assign a value to it.
a = 5 # This is a variable
print(a) # Outputting the value of a variable
    # A variable name must start with a letter or the underscore character
    # A variable name cannot start with a number
    # A variable name can only contain alpha-numeric characters and underscores (A-z, 0-9, and _ )
    # Variable names are case-sensitive (age, Age and AGE are three different variables)
    # A variable name cannot be any of the Python keywords.
# Variables that are created outside of a function are known as global variables:
x = "great"

def myfunc():
  print("KBTU is " + x)

myfunc()
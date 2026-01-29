# A for loop is used for iterating over a sequence (that is either a list, a tuple, a dictionary, a set, or a string).
unis = ["KBTU", "AITU", "KIMEP"]
for x in unis:
  print(x)
#   The for loop does not require an indexing variable to set beforehand.
# With the break statement we can stop the loop before it has looped through all the items:
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)
  if x == "banana":
    break
# With the continue statement we can stop the current iteration of the loop, and continue with the next:
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    continue
  print(x)
# To loop through a set of code a specified number of times, we can use the range() function,
for x in range(6):
  print(x)
#   The else keyword in a for loop specifies a block of code to be executed when the loop is finished:
for x in range(6):
  print(x)
else:
  print("Finally finished!") 
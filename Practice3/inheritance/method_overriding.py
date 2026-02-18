#We want to add the __init__() function to the child class (instead of the pass keyword).
class Student(Person):
    def __init__(self, fname, lname):
#add properties etc. 
# When you add the __init__() function, the child class will no longer inherit the parent's __init__() function.
# The child's __init__() function overrides the inheritance of the parent's __init__() function.
# To keep the inheritance of the parent's __init__() function, add a call to the parent's __init__() function:
# class Student(Person):
#     def __init__(self, fname, lname):
#         Person.__init__(self, fname, lname)
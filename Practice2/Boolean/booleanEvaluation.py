# bool() function allows evaluating any value and returns True or False
print(bool("Hello")) # True
print(bool(15)) # True
# Almost any value is evaluated to True if it has some sort of content.
"""
Any string is True, except empty strings.

Any number is True, except 0.

Any list, tuple, set, and dictionary are True, except empty ones.
"""
# All the following are false:
bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({}) 
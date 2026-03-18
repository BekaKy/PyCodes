from functools import reduce
numbers = [1, 2, 3, 4, 5, 6]
squared = list(map(lambda x: x**2, numbers))
print(squared)

evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)


product = reduce(lambda x, y: x * y, [1, 2, 3, 4, 5])
print(product)
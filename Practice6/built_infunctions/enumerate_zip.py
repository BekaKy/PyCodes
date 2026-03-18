names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]

for i, name in enumerate(names):
    print(f"{i}: {name}")

for name, age in zip(names, ages):
    print(f"{name} is {age}")

val = "42"
print(type(val) is str)
print(isinstance(val, int))
val_int = int(val)
val_float = float(val)
val_list = list(val)
print(val_int)
print(val_float)
print(val_list)
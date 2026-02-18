# Multiple inheritance in Python allows a class to derive features from more than one parent class.
class Flyer:
    def fly(self):
        return "I am soaring!"

class Swimmer:
    def swim(self):
        return "I am paddling!"

class Duck(Flyer, Swimmer):
    pass

donald = Duck()
print(donald.fly())  
print(donald.swim())  

class LoggerMixin:
    def log(self, message):
        print(f"[LOG]: {message}")

class Database:
    def save(self):
        print("Saving data to disk...")

class SecureDatabase(Database, LoggerMixin):
    def save(self):
        self.log("Backup started.")
        super().save()

db = SecureDatabase()
db.save() 

class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower

class Body:
    def __init__(self, color):
        self.color = color

class Car(Engine, Body):
    def __init__(self, horsepower, color, brand):
        # Initializing both parents manually or via super
        Engine.__init__(self, horsepower)
        Body.__init__(self, color)
        self.brand = brand

my_car = Car(450, "Red", "Ferrari")
print(f"{my_car.brand}: {my_car.horsepower}hp, {my_car.color}")
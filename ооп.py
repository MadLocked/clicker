class Transport:
    def __init__(self, color, model, speed):
        self.color = color
        self.model = model
        self.speed = speed
    def j(self):
        print('You have a transport, great!')

class Car(Transport):
    def time_to_get(self, km):
        print(f'{km / self.speed} hours to get there')

car1 = Car('red', 'Porsche', 100)
# car1.j()
# car1.time_to_get(int(input('Enter distance in km: ')))

class Animal:
    def __init__(self, sound, food, name):
        self.sound = sound
        self.food = food
        self.name = name

    def sound(self):
        print(self.sound)
    

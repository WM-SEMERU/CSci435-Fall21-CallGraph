# import pyan
# from IPython.display import HTML
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput


class Vehicle:
    def __init__(self, brand, model, type):
        self.brand = brand
        self.model = model
        self.type = type
        self.gas_tank_size = 14
        self.fuel_level = 0

    def fuel_up(self):
        self.fuel_level = self.gas_tank_size
        print('Gas tank is now full.')
        self.read_to_drive()

    def drive(self):
        print(f'The {self.model} is now driving.')
        

    def read_to_drive(self):
        if(self.fuel_level == self.gas_tank_size):
            self.drive()
            return True
        else:
            return False
    
    def check_brand(self):
        maker = Automaker()
        brand = maker.get_brand(self)
        print(brand)


class Automaker():

    def __init__(self):
        self.car = None
    
    def get_brand(self, car):
        if(car.brand == 'Honda'):
            print('Car is made from Japansese Automaker')
            return 'Japan'
        
def main():
    graphviz = GraphvizOutput()
    graphviz.output_file = 'basic.png'

    with PyCallGraph(output=graphviz):
        car = Vehicle('Honda','Accord', type)
        car.check_brand()
        car.fuel_up()

car = Vehicle('Honda','Accord', type)
car.check_brand()

if __name__ == '__main__':
    main()
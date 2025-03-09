#Определите класс Rectangle, который представляет прямоугольник. Через конструктор класс принимает ширину и длину и 
#сохраняет их в атрибутах width и length соответственно. Также этом классе определите метод area, который возвращает 
#площадь прямоугольника, и метод perimeter, который возвращает периметра прямоугольника.

#После создания класса определите несколько объектов класса Rectangle и продемонстрируйте работу его методов.

class Rectangle:

    def __init__(self, width, lenght):
        self.width = width
        self.lenght = lenght
    
    def area(self):
        return(self.width*self.lenght) 

    def perimetr(self):
        return((self.width+self.lenght)*2)
    
tr = Rectangle(5, 7)
print('Выводит площадь прямоугольника:', tr.area())
print('Выводит перимерт прямоугольника:', tr.perimetr())
print(tr.lenght*tr.width)

#Создайте класс BankAccount, который представляет банковский счет. Определите в этом классе атрибуты account_number и balance, 
#которые представляют номер счета и баланс. Через параметры конструктора передайте этим атрибутам начальные значения.

#Также в классе определите метод add, который принимает некоторую сумму и добавляет ее на баланс счета. И определите метод 
#withdraw, который принимает некоторую сумму и снимает ее с баланса. При этом с баланса нельзя снять больше, чем имеется. 
#Если на балансе недостаточно средств, то пользователю должно выводиться соответствующее сообщение.

class BankAccount:
    def __init__(self, account_number, balance):
        self.account_number = account_number
        self.balance = balance

    def add(self,summa):
        self.balance=self.balance+summa
    def withdraw(self,summa):
        if summa<self.balance:
            self.balance=self.balance-summa
        else:
            print('Операция невозможна!') 

shet = BankAccount(1234, 500)
print('На счёте было:', shet.balance)
shet.add(100)
print('На счёте стало:', shet.balance)
shet.withdraw(400)
print('На счёте стало:', shet.balance)
shet.withdraw(400)
print('На счёте стало:', shet.balance)
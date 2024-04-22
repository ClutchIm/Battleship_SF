from random import randint
from time import sleep


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return f'Выход из доски\n{'-'*30}'


class BoardUsedException(BoardException):
    def __str__(self):
        return f'Вы уже стреляли в эту клетку\n{'-'*30}'


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot ({self.y}, {self.x})'


class Ship:
    def __init__(self, length, pos,  route):
        self.length = length
        self.route = route
        self.pos = pos

        self.health = length

    def dots(self):
        ship_dots = []
        dot_x = self.pos.x
        dot_y = self.pos.y

        for i in range(self.length):
            ship_dots.append(Dot(dot_x, dot_y))
            if self.route == 0:
                dot_x += 1
            elif self.route == 1:
                dot_y += 1

        return ship_dots


class Board:
    def __init__(self, hide=False, size=6):
        self.hide = hide
        self.size = size

        self.field = [['O'] * size for _ in range(size)]

        self.busy = []
        self.ships = []

        self.lives = 0

    def add_ship(self, ship):
        for d in ship.dots():
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        for d in ship.dots():
            self.field[d.y-1][d.x-1] = '■'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship):
        cont = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]
        for i in ship.dots():
            for j in cont:
                contour = Dot(i.x + j[0], i.y + j[1])
                if contour in ship.dots() or contour in self.busy or self.out(contour):
                    pass
                else:
                    self.busy.append(contour)
                    self.field[contour.y - 1][contour.x - 1] = '.'

    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'

        if self.hide:
            res = res.replace('■', 'O')
        return res

    def out(self, d):
        result = False
        if d.x > self.size or d.x < 1:
            result = True
        elif d.y > self.size or d.y < 1:
            result = True
        return result

    def shot(self, d):
        if self.out(d):
            raise BoardOutException
        if d in self.busy:
            raise BoardUsedException

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots():
                if ship.health > 1:
                    ship.health -= 1
                    print(f'{'-'*30}\nРанил!')
                else:
                    self.lives -= 1
                    print(f'{'-'*30}\nУбил!')
                    self.contour(ship)

                self.field[d.y-1][d.x-1] = 'X'
                return True

        print(f'{'-'*30}\nМимо')
        self.field[d.y-1][d.x-1] = '.'

        return False

    def begin(self):
        self.busy = []
        self.lives = len(self.ships)
        for i in range(len(self.field)):
            for j in range(len(self.field)):
                if self.field[i][j] == '.':
                    self.field[i][j] = 'O'


class Player:
    def __init__(self, own_board, op_board, difficulty=0):
        self.own_board = own_board
        self.op_board = op_board

        self.difficulty = difficulty
        self.hard = 0
        self.hard_50 = 0

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                result = self.op_board.shot(target)
                return result
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = 0

        if self.hard:
            if randint(0, self.difficulty):
                d = self.hard
                self.hard = 0
            else:
                d = self.hard_50

                if self.hard_50 == self.hard:
                    self.hard = 0
                self.hard_50 = self.hard

        if self.difficulty:
            if not d:
                d = Dot(randint(1, 6), randint(1, 6))

                for ships in self.op_board.ships:
                    if d in ships.dots() and ships.health > 1:
                        self.cont(d)
        else:
            d = Dot(randint(1, 6), randint(1, 6))

        if not (d in self.op_board.busy):
            print(f'Ход AI ({d.y}, {d.x})')

        return d

    def cont(self, d):
        own_d = [
            (-1, 0), (1, 0),
            (0, -1), (0, 1)
        ]
        for i in own_d:
            contour = Dot((d.x + i[0]), (d.y + i[1]))

            for ships in self.op_board.ships:
                if contour in ships.dots():
                    self.hard = contour
                else:
                    if self.hard:
                        if contour == self.hard:
                            pass
                        else:
                            self.hard_50 = contour
                    else:
                        self.hard_50 = contour


class User(Player):
    def ask(self):
        while True:
            cord = input(f'Ваш ход: ').split()

            if len(cord) != 2:
                print(f'Введите 2 координаты! \n{'-'*30}')
                continue

            x, y = cord

            if not (x.isdigit()) or not (y.isdigit()):
                print(f'Введите числа! \n{'-'*30}')
                continue

            x, y = int(x), int(y)

            return Dot(y, x)


class Game:
    def __init__(self, size=6):
        self.size = size

        self.user_board = self.random_board(False)
        self.ai_board = self.random_board(True)

        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

    def random_board(self, hide):
        board = None
        while board is None:
            board = self.random_place(hide)
        board.begin()
        return board

    def random_place(self, hide):
        count_ships = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size, hide=hide)
        attempts = 0
        for s in count_ships:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(s, Dot(randint(1, self.size), randint(1, self.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        return board

    @staticmethod
    def greet():
        sleep(0.5)
        print(f'-'*30)
        print(f'Добро пожаловать в игру')
        print(f'    "Морской бой"')
        print(f'-'*30)
        sleep(2)
        print(f'Формат ввода x, y:')
        print(f'x - строка')
        print(f'→'*11)
        print(f'-'*30)
        print(f'y - столбец')
        print(f'↓'*11)
        sleep(3)

    def show(self):
        print(f'\n')
        print(f'-'*30)
        print(f'\tВаша доска:\n{self.user_board}\n\n\tДоска противника:\n{self.ai_board}\n')
        print(f'-'*30)

    def loop(self):
        turn = 'User'
        self.show()

        while True:
            sleep(1)

            if self.ai_board.lives == 0:
                print('Вы победили!')
                break

            if self.user_board.lives == 0:
                print('К сожалению вы проиграли')
                break

            if turn == 'User':
                turn = 'AI'
                if self.user.move():
                    turn = 'User'

                self.show()
            else:
                turn = 'User'
                if self.ai.move():
                    turn = 'AI'

                self.show()

    def difficulty(self):
        print(f'\n{'-' * 60}')
        print('''
            Вы можете выбрать сложность.
                   Всего их 3.
        ''')
        sleep(2)
        print('-'*60)
        print('''
        \t1 - самая простая, в ней компьютер
        будет стрелять наугад.
        \t2 - средняя, в ней компьютер с 50%
        шансом при ранении выстрелит в соседнюю
        клетку корабля.
        \t3 - более сложная, с ней компьютер
        при ранении скорее всего поразит соседнюю
        клетку корабля.
        ''')
        while True:
            choose = input(f'{'-'*60}\nДля выбора выберите цифру от 1 до 3:').split()
            if len(choose) > 1:
                print(f'{'-'*60}\nВведите 1 цифру')
                continue

            c = choose[0]

            if not (c.isdigit()):
                print(f'{'-'*60}\nВведите цифру')
                continue

            c = int(c)-1

            if c in list(range(3)):
                self.ai = AI(self.ai_board, self.user_board, c)
                break

    def start(self):
        self.greet()
        self.difficulty()
        self.loop()


game = Game()
game.start()

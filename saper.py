"""Игра Сапер1."""
from random import randint

import pygame as pg

# Количество ячеек на поле.
BOARD_CELL_COUNT = 10

# Количество бомб.
BOMBS_COUNT = 10

# Константы для размеров экрана и сетки (кратно GRID_SIZE):
GRID_SIZE = 30
SCREEN_WIDTH = SCREEN_HEIGHT = BOARD_CELL_COUNT * GRID_SIZE
GRID_WIDTH = GRID_HEIGHT = SCREEN_WIDTH // GRID_SIZE

# Размер поля.
BOARD_SIZE = GRID_SIZE * BOARD_CELL_COUNT

# Координаты поля.
X = Y = 0
X_END = Y_END = BOARD_SIZE
BOARD_POSITION = (X, Y, X_END, Y_END)

# Направления клеток.
DESTINATIONS = ((-1, -1), (0, -1), (1, -1),
                (-1, 0), (1, 0),
                (-1, 1), (0, 1), (1, 1))


# Цвет фона - белый.
BOARD_BACKGROUND_COLOR = (255, 255, 225)

# Цвет границы ячейки - голубой.
BORDER_COLOR = (93, 216, 228)

# Цвет скрытой ячейки - зеленый.
HIDEN_COLOR = (50, 205, 50)

# Цвета цифр.
NUMBER_COLOR = {1: (0, 0, 255),  # синий
                2: (81, 200, 120),  # зеленый
                3: (255, 0, 0),  # красный
                4: (139, 0, 255),  # фиолетовый
                5: (255, 165, 0),  # оранжевый
                6: (255, 255, 0),  # желтый
                7: (0, 191, 255),  # голубой
                8: (0, 0, 0)  # черный
                }

# Цвет бомбы - черный.
BOMB_COLOR = (0, 0, 0)

# Цвет флага - красный.
FLAG_COLOR = (255, 0, 0)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Сапер')


class GameObject:
    """Класс, описывающий все объекты игры."""

    def __init__(self, body_color=None):
        """Метод - инициализатор объекта класса."""
        self.body_color = body_color

    def draw(self):
        """Метод для отрисовки объектов."""
        raise NotImplementedError(
            f'Определите draw в {type(self)}'
        )

    def draw_cell(self, cell_position=None, cell_color=None):
        """Метод отрисовывает одну ячейку на поле."""
        cell = pg.Rect(cell_position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, cell_color, cell)
        pg.draw.rect(screen, BORDER_COLOR, cell, 1)

    def draw_flag(self, cell_position=None, cell_color=None):
        """Метод отрисовывает флаг."""
        x, y = cell_position
        pg.draw.polygon(screen,
                        cell_color,
                        [[x, y], [x + GRID_SIZE, y + GRID_SIZE // 2],
                         [x, y + GRID_SIZE]])

    def draw_bomb(self, cell_position=None, cell_color=None):
        """Метод отрисовывает бомбу."""
        x, y = cell_position
        pg.draw.circle(screen,
                       cell_color,
                       (x + GRID_SIZE // 2, y + GRID_SIZE // 2),
                       GRID_SIZE // 3 - GRID_SIZE // 5)

    def draw_number(self, cell_position=None, cell_color=None, text=None):
        """Метод отрисовывает число бомб рядом."""
        f1 = pg.font.Font(None, 36)
        text1 = f1.render(str(text), True, cell_color)
        screen.blit(text1, cell_position)


class Board(GameObject):
    """Дочерний класс, описывающий поле."""

    flag_count = BOARD_CELL_COUNT

    def __init__(self, board_position=None, body_color=None):
        """Метод - инициализатор объекта дочернего класса Board."""
        super().__init__(body_color)
        self.board_position = board_position
        self.empty_cells_stack = []
        self.bombs_positions = []
        # Создаем список списков значений каждой клетки поля и заполняем их.
        self.cell = [[0] * BOARD_CELL_COUNT for _ in range(BOARD_CELL_COUNT)]
        for i in range(BOARD_CELL_COUNT):
            for j in range(BOARD_CELL_COUNT):
                self.cell[i][j] = {
                                    'bomb_count': 0,  # 0 - пустая.
                                    'bomb': False,
                                    'hiden': True,
                                    'flag': False
                                    }

    def open_around_cells(self, board, x, y):
        """Метод открывает клетки до цифр вокруг заданной."""
        # Добавляем заданную клетку в стек.
        board.empty_cells_stack.append((x, y))
        # Пока стек заполнен:
        while board.empty_cells_stack:
            # Берем координаты последней клетки в стеке, отмечаем ее
            # проверенной и удаляем из стека.
            x, y = board.empty_cells_stack[-1]
            board.cell[x][y]['bomb_count'] = -1
            board.empty_cells_stack.pop()
            # Проходимся по окрестности Мура.
            for x_coef, y_coef in DESTINATIONS:
                x_new = x + x_coef
                y_new = y + y_coef
                # Проверка на границы поля.
                if (0 <= x_new < BOARD_CELL_COUNT and
                        0 <= y_new < BOARD_CELL_COUNT):
                    board.cell[x_new][y_new]['hiden'] = False
                    # Если клетка пустая, добавляем ее в стек для проверки.
                    if board.cell[x_new][y_new]['bomb_count'] == 0:
                        board.empty_cells_stack.append((x_new, y_new))

    def place_random_bombs(self):
        """Метод случайно расставляет бомбы на поле."""
        cur_bombs = 0
        while cur_bombs != BOMBS_COUNT:
            x = randint(0, BOARD_CELL_COUNT - 1)
            y = randint(0, BOARD_CELL_COUNT - 1)
            if not self.cell[x][y]['bomb']:
                self.cell[x][y]['bomb'] = True
                self.bombs_positions.append((x, y))
                cur_bombs += 1

    def get_bomb_count_around_cell(self):
        """Метод записывает количество бомб вокруг клетки."""
        # Проходимся по каждой бомбе.
        for x, y in self.bombs_positions:
            # Проходимся по окрестности Мура бомбы.
            for x_coef, y_coef in DESTINATIONS:
                x_new = x + x_coef
                y_new = y + y_coef
                # Проверка на границы поля.
                if (0 <= x_new < BOARD_CELL_COUNT and
                        0 <= y_new < BOARD_CELL_COUNT):
                    self.cell[x_new][y_new]['bomb_count'] += 1

    def draw(self):
        """Метод отрисовывает объект Поле."""
        for i in range(BOARD_CELL_COUNT):
            for j in range(BOARD_CELL_COUNT):
                self.draw_cell((i * GRID_SIZE, j * GRID_SIZE),
                               BOARD_BACKGROUND_COLOR)
                if self.cell[i][j]['hiden'] is True:
                    self.draw_cell((i * GRID_SIZE, j * GRID_SIZE), HIDEN_COLOR)
                    if self.cell[i][j]['flag'] is True:
                        self.draw_flag((i * GRID_SIZE, j * GRID_SIZE),
                                       FLAG_COLOR)
                elif self.cell[i][j]['bomb'] is True:
                    self.draw_bomb((i * GRID_SIZE, j * GRID_SIZE), BOMB_COLOR)
                elif self.cell[i][j]['bomb_count'] > 0:
                    self.draw_number((
                        i * GRID_SIZE, j * GRID_SIZE),
                        NUMBER_COLOR[self.cell[i][j]['bomb_count']],
                        self.cell[i][j]['bomb_count'])


def handle_keys(board):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit('Пользователь завершил игру.')
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_x = event.pos[0]
            mouse_y = event.pos[1]
            x = mouse_x // GRID_SIZE
            y = mouse_y // GRID_SIZE
            # Если нажата правая кнопка мыши.
            if event.button == 3:
                if board.cell[x][y]['flag']:
                    board.cell[x][y]['flag'] = False
                    board.flag_count += 1
                # Флаг можно поставить при его наличии и если ячейка скрыта.
                elif board.flag_count > 0 and board.cell[x][y]['hiden']:
                    board.cell[x][y]['flag'] = True
                    board.flag_count -= 1
            # Если нажата левая кнопка мыши, ячейка скрыта и нет флага.
            elif (event.button == 1 and board.cell[x][y]['hiden'] and not
                    board.cell[x][y]['flag']):
                # Ячейка с бомбой - открываем вся клетки.
                if board.cell[x][y]['bomb'] is True:
                    for x in range(BOARD_CELL_COUNT):
                        for y in range(BOARD_CELL_COUNT):
                            board.cell[x][y]['hiden'] = False
                # Пустая ячейка - открывается периметр из чисел.
                elif board.cell[x][y]['bomb_count'] == 0:
                    board.open_around_cells(board, x, y)
                # Ячейка с цифрой
                elif board.cell[x][y]['bomb_count'] > 0:
                    board.cell[x][y]['hiden'] = False


def main():
    """Главная функция игры."""
    # Инициализация PyGame:
    pg.init()

    board = Board(BOARD_POSITION, BOARD_BACKGROUND_COLOR)
    board.place_random_bombs()
    board.get_bomb_count_around_cell()
    # Основной цикл игры.
    while True:
        handle_keys(board)
        board.draw()
        pg.display.flip()
        pg.display.update()


if __name__ == '__main__':
    main()

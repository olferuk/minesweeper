import numpy as np


class Cell:
    def __init__(self, has_mine: bool = False, has_flag: bool = False, is_opened: bool = False):
        self.has_mine = has_mine
        self.has_flag = has_flag
        self.is_opened = is_opened
        self.num_mines_around = 0


class MinesweeperField:
    def __init__(self, rows: int, cols: int, mines: int) -> None:
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.field = []
        self.create()

    def create(self):
        self.reset()
        self.populate()
        self.count_mines()

    def __getitem__(self, key):
        return self.field[key]

    def reset(self):
        self.field = []
        for _ in range(self.cols):
            row = []
            for _ in range(self.rows):
                row.append(Cell(has_mine=False))
            self.field.append(row)

    def populate(self):
        mines = np.random.choice(self.rows * self.cols, self.mines, replace=False)
        for mine in mines:
            row = mine // self.rows
            col = mine % self.rows
            self.field[row][col].has_mine = True

    def count_mines(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.field[row][col].has_mine:
                    continue
                self.field[row][col].num_mines_around = self._count_mines_around(row, col)

    def open(self, cell_position) -> bool:
        """Returns True if the game is still live, False otherwise"""
        col, row = cell_position
        if self._should_not_process(row, col):
            return True
        cell = self.field[row][col]
        # left click on the opened cell with the number of mines around should open all cells
        # around if the number of flags around is equal to the number of mines around
        if cell.is_opened:
            if (
                cell.num_mines_around > 0
                and self._count_flags_around(row, col) == cell.num_mines_around
            ):
                return self._open_forcefully(row, col)
            return True
        # left click on the flag result in nothing for safety
        if cell.has_flag:
            return True
        if cell.has_mine:
            cell.is_opened = True
            return False
        # open a cell if it has mines around, but only one
        if cell.num_mines_around > 0:
            cell.is_opened = True
        # otherwise unroll all cells around
        else:
            self._bsf_open(row, col)
        return True

    def flag(self, cell_position):
        col, row = cell_position
        if self._should_not_process(row, col):
            return
        # put a flag only if isn't opened
        if not self.field[row][col].is_opened:
            self.field[row][col].has_flag = not self.field[row][col].has_flag

    def put_flags_on_mines(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.field[row][col].has_mine:
                    self.field[row][col].has_flag = True

    def _count_mines_around(self, row: int, col: int) -> int:
        num_mines = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if self._should_not_process(row + i, col + j):
                    continue
                if self.field[row + i][col + j].has_mine:
                    num_mines += 1
        return num_mines

    def _count_flags_around(self, row: int, col: int) -> int:
        num_flags = 0
        for v in self._all_neighbours:
            if self._should_not_process(row + v[0], col + v[1]):
                continue
            if self.field[row + v[0]][col + v[1]].has_flag:
                num_flags += 1
        return num_flags

    def _count_closed_cells(self) -> int:
        num_closed = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.field[row][col].is_opened:
                    num_closed += 1
        return num_closed

    def _open_forcefully(self, row: int, col: int) -> bool:
        """Return True if the game is still live, False otherwise"""
        still_live = True
        for v in self._all_neighbours:
            # skip if out of bounds
            if self._should_not_process(row + v[0], col + v[1]):
                continue
            neighbor_cell = self.field[row + v[0]][col + v[1]]
            # skip the flagged cells
            if neighbor_cell.has_flag:
                continue
            # open the cell
            self._bsf_open(row + v[0], col + v[1])
            if neighbor_cell.has_mine and not neighbor_cell.has_flag:
                still_live = False
        return still_live

    def _bsf_open(self, row: int, col: int):
        # use breadth-first search to open all cells around with 0 mines around
        queue = [(row, col)]
        visited = set()
        while len(queue) > 0:
            row, col = queue.pop(0)
            visited.add((row, col))
            if self._should_not_process(row, col):
                continue
            if self.field[row][col].is_opened:
                continue
            self.field[row][col].is_opened = True
            self.field[row][col].has_flag = False
            if self.field[row][col].num_mines_around == 0:
                for v in self._all_neighbours:
                    p = (row + v[0], col + v[1])
                    if p in visited:
                        continue
                    queue.append(p)

    @property
    def _all_neighbours(self):
        return [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def _should_not_process(self, row: int, col: int) -> bool:
        return row < 0 or col < 0 or row >= self.rows or col >= self.cols

    def check_win(self) -> bool:
        return self.mines == self._count_closed_cells()

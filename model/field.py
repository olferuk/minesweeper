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
        for _ in range(self.rows):
            row = []
            for _ in range(self.cols):
                row.append(Cell(has_mine=False))
            self.field.append(row)

    def populate(self):
        mines = np.random.choice(self.rows * self.cols, self.mines, replace=False)
        for mine in mines:
            row = mine // self.cols
            col = mine % self.cols
            self.field[row][col].has_mine = True

    def count_mines(self):
        with self.all_cells() as cell_info:
            for cell, row, col in cell_info:
                cell.num_mines_around = self.count_neighbors_predicate(
                    row, col, lambda cell: cell.has_mine
                )

    # --- UI ---

    def open(self, cell_position) -> bool:
        """Returns True if the game is still live, False otherwise"""
        col, row = cell_position
        if self._should_not_process(row, col):
            return True
        cell = self.field[row][col]

        # left click on the opened cell with the number of mines around should open all cells
        # around if the number of flags around is equal to the number of mines around
        if cell.is_opened:
            num_flags = self.count_neighbors_predicate(row, col, lambda cell: cell.has_flag)
            if cell.num_mines_around > 0 and num_flags == cell.num_mines_around:
                return self._open_forcefully(row, col)
            return True

        # left click on the flag result in nothing for safety
        if cell.has_flag:
            return True

        # click on the mine = game over
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
        cell = self.field[row][col]
        if not cell.is_opened:
            cell.has_flag = not cell.has_flag

    def put_flags_on_mines(self):
        with self.all_cells() as cells:
            for cell, _, _ in cells:
                if cell.has_mine:
                    cell.has_flag = True

    def check_win(self) -> bool:
        return self.mines == self.count_predicate(lambda cell: not cell.is_opened)

    # --- Context managers ---

    def all_cells(self):
        class CellIterator:
            def __init__(self, field):
                self.field = field
                self.row = 0
                self.col = 0

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                pass

            def __iter__(self):
                return self

            def __next__(self):
                if self.row >= self.field.rows:
                    raise StopIteration
                cell = self.field[self.row][self.col]
                row, col = self.row, self.col
                self.col += 1
                if self.col >= self.field.cols:
                    self.row += 1
                    self.col = 0
                return (cell, row, col)

        return CellIterator(self)

    def all_neighbours(self, row, col):
        class NeighbourIterator:
            def __init__(self, field, row, col):
                self.field = field
                self.row = row
                self.col = col
                self.i = 0

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                pass

            def __iter__(self):
                return self

            def __next__(self):
                while True:
                    if self.i >= len(self.field._d8):
                        raise StopIteration
                    v = self.field._d8[self.i]
                    self.i += 1
                    row = self.row + v[0]
                    col = self.col + v[1]
                    if self.field._should_not_process(row, col):
                        continue
                    cell = self.field[row][col]
                    return (cell, row, col)

        return NeighbourIterator(self, row, col)

    def count_predicate(self, predicate):
        with self.all_cells() as cell_info:
            count = sum([1 for (cell, _, _) in cell_info if predicate(cell)])
        return count

    def count_neighbors_predicate(self, row, col, predicate):
        with self.all_neighbours(row, col) as neigbours_info:
            count = sum([1 for (n, _, _) in neigbours_info if predicate(n)])
        return count

    # --- Private methods ---

    def _open_forcefully(self, row: int, col: int) -> bool:
        """Return True if the game is still live, False otherwise"""
        still_live = True
        for v in self._d8:
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
            cell = self.field[row][col]
            if cell.is_opened:
                continue
            cell.is_opened = True
            cell.has_flag = False
            if cell.num_mines_around == 0:
                for v in self._d8:
                    p = (row + v[0], col + v[1])
                    if p in visited:
                        continue
                    queue.append(p)

    @property
    def _d8(self):
        return [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def _should_not_process(self, row: int, col: int) -> bool:
        return row < 0 or col < 0 or row >= self.rows or col >= self.cols

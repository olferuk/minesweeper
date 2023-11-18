# Minesweeper

Written in Pygame.

## How to play a minesweeper game?

The goal of the game is to open all cells but those with mines. The cells may contain a mine, or a number denoting the number of adjacent mines (diagonals included), or just be empty.

The first click on a new field is guaranteed to be safe.

Controls:
* `SPACE` — Restart game and create a new field.
* `RIGHT MOUSE CLICK` — Denote cell with a flag to make it safe.
* `LEFT MOUSE CLICK` — Opens a closed cell. Or, when clicked a cell with number, opens all neighboring cells, except cells with flags.

## How to install?

```bash
make install
# or
pip install -r requirements.txt
```

## How to play?

```bash
make play
# or
python main.py
```

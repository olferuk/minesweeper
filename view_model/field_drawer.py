from pygame import Surface, draw, font
import numpy as np


class FieldDrawer:
    def __init__(self, field, config) -> None:
        self.field = field
        self.cfg = config.field_draw
        self._calculate_field_size(config, field)
        self._calculate_font_size(config)
        self.highlighted_cell = (-1, -1)

    def draw(self, screen: Surface):
        x0, y0 = self.origin
        for row in range(self.field.rows):
            for col in range(self.field.cols):
                x = col * self.cell_size + x0
                y = row * self.cell_size + y0
                self.draw_cell(
                    screen,
                    x,
                    y,
                    self.field[row][col],
                    highlighted=(col, row) == self.highlighted_cell,
                )

    def draw_cell(self, screen: Surface, x: int, y: int, cell, highlighted: bool = False):
        ss = self.cell_size
        colors = self.cfg.colors

        # draw a cell background
        if cell.is_opened and cell.has_mine:
            color = colors.mine_cell
        elif cell.is_opened:
            color = colors.cell_opened
        else:
            color = colors.cell_hovered if highlighted else colors.cell
        draw.rect(screen, color, (x, y, ss, ss))

        # draw foreground
        if cell.has_mine and cell.is_opened:
            s0 = ss / 5
            ox, oy = x + ss / 2, y + ss / 2
            draw.line(screen, colors.mine, (ox, y + s0), (ox, y + ss - s0), 3)
            draw.line(screen, colors.mine, (x + s0, oy), (x + ss - s0, oy), 3)
            llen = ss - 2 * s0
            draw.line(
                screen,
                colors.mine,
                (ox + llen / 4 * np.sqrt(2), oy + llen / 4 * np.sqrt(2)),
                (ox - llen / 4 * np.sqrt(2), oy - llen / 4 * np.sqrt(2)),
                3,
            )
            draw.line(
                screen,
                colors.mine,
                (ox + llen / 4 * np.sqrt(2), oy - llen / 4 * np.sqrt(2)),
                (ox - llen / 4 * np.sqrt(2), oy + llen / 4 * np.sqrt(2)),
                3,
            )
            draw.circle(screen, colors.mine, (ox, oy), ss / 4)
            draw.circle(screen, colors.mine_flare, (ox - ss / 11, oy - ss / 11), ss / 10)
            draw.circle(screen, colors.mine_flare, (ox - ss / 11, oy - ss / 11), ss / 10)
            draw.circle(screen, colors.mine_flare_center, (ox - ss / 11, oy - ss / 11), ss / 15)

        elif cell.is_opened and cell.num_mines_around > 0:
            label = self.font.render(f"{cell.num_mines_around}", True, (0, 0, 0))
            screen.blit(
                label, (x + ss / 2 - label.get_width() / 2, y + ss / 2 - label.get_height() / 2)
            )

        if cell.has_flag:
            s0 = ss / 5
            draw.polygon(
                screen,
                colors.flag,
                [(x + s0, y + s0), (x + s0, y + ss - s0), (x + ss - s0, y + ss / 2)],
            )

        # draw a cell border
        draw.rect(screen, colors.border, (x, y, ss, ss), 1)

    def _calculate_font_size(self, config):
        size = config.field_draw.font.size
        size = int(self.cell_size * 0.75) if size == "adaptive" else size
        self.font = font.SysFont(self.cfg.font.name, size)

    def _calculate_field_size(self, config, field):
        margin = config.field_draw.field_margin

        if config.field_draw.cell_size == "adaptive":
            # the screen is horizontal — fitting the height first
            if config.screen.width > config.screen.height:
                space = config.screen.height - margin * 2
                self.cell_size = int(space / field.rows)
            # the screen is vertical — fitting the width first
            else:
                space = config.screen.width - margin * 2
                self.cell_size = int(space / field.cols)
                # print(space, self.cell_size, self.cell_size*field.cols, self.cell_size*field.rows)
        else:
            self.cell_size = config.field_draw.cell_size

        # setting the point of origin
        self.origin = (
            (config.screen.width - field.cols * self.cell_size) // 2,
            (config.screen.height - field.rows * self.cell_size) // 2,
        )

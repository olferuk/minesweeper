import pygame

import pygame.locals as events
from pygame.locals import QUIT
from game import GameBuilder
from sys import exit

pygame.init()

builder = GameBuilder()
screen = builder.build_screen()
field, field_drawer = builder.build_field(level_number=4)

mouse_pos = (0, 0)
mouse_cell = (-1, -1)
field_is_blocked = False
safe_click = True


while True:
    screen.fill(builder.config.screen.background_color)
    field_drawer.draw(screen)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

        elif event.type == events.MOUSEMOTION:
            # is the mouse shift was at least for one whole pixel
            if event.pos != mouse_pos:
                # TODO: move this logic outta here
                mouse_pos = event.pos
                x, y = mouse_pos

                ss = field_drawer.cell_size
                x0, y0 = field_drawer.origin

                cell_x, cell_y = int((x - x0) / ss), int((y - y0) / ss)
                mouse_cell = (cell_x, cell_y)
                field_drawer.highlighted_cell = (cell_x, cell_y)

        elif event.type == events.MOUSEBUTTONDOWN:
            if not field_is_blocked:
                # left click
                if event.button == 1:
                    if safe_click:
                        while True:
                            still_live = field.open(mouse_cell)
                            if still_live:
                                safe_click = False
                                break
                            field.create()
                    else:
                        still_live = field.open(mouse_cell)

                    if not still_live:
                        print("You lose!")
                        field_is_blocked = True

                # right click
                elif event.button == 3:
                    field.flag(mouse_cell)

                if field.check_win():
                    print("You win!")
                    field.put_flags_on_mines()
                    field_is_blocked = True

        elif event.type == events.KEYDOWN:
            if event.key == events.K_SPACE:
                print("--- Starting a new game ---")
                field.create()
                field_is_blocked = False
                safe_click = True

    pygame.display.update()

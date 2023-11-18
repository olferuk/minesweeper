from dynaconf import Dynaconf
from model.field import MinesweeperField
from view_model.field_drawer import FieldDrawer
from typing import Tuple

import pygame


class GameBuilder:
    # singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(GameBuilder, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.config = Dynaconf(
            root_path="configs",
            settings_files=[
                "game.yml",
                "levels.yml",
            ],
        )

    def build_screen(self) -> pygame.Surface:
        cfg = self.config.screen
        screen = pygame.display.set_mode(
            [cfg.width, cfg.height],
            0,
            cfg.color_bits,
        )
        pygame.display.set_caption(cfg.title)
        return screen

    def build_field(self, level_number: int) -> Tuple[MinesweeperField, FieldDrawer]:
        level = getattr(self.config, f"lvl_{level_number}")
        field = MinesweeperField(level.rows, level.cols, level.mines)
        field_drawer = FieldDrawer(field, self.config)
        return field, field_drawer

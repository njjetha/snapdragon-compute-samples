# -----------------------------------------------------------------------------
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
#
# -----------------------------------------------------------------------------


import pygame
from typing import Tuple, Any


class GameConfig():
    def _rgb_to_tuple(self, rgb: dict[str, int]) -> Tuple[int, int, int]:
        return (rgb["red"], rgb["green"], rgb["blue"])

    def _tuple_to_rgb(self, t: Tuple[int, int, int]) -> dict[str, int]:
        return {
            "red": t[0],
            "green": t[1],
            "blue": t[2]
        }

    def __init__(self, config_dict: dict) -> None:
        self.player_1_paddle_width: int = config_dict["player_1_paddle_width"]
        self.player_1_paddle_height: int = config_dict["player_1_paddle_height"]
        self.player_2_paddle_width: int = config_dict["player_2_paddle_width"]
        self.player_2_paddle_height: int = config_dict["player_2_paddle_height"]
        self.ball_radius: int = config_dict["ball_radius"]

        self.background_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["background_color"])
        self.ball_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["ball_color"])
        self.player_1_paddle_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["player_1_paddle_color"])
        self.player_2_paddle_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["player_2_paddle_color"])
        self.text_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["text_color"])
        self.text_background_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["text_background_color"])

        self.player_1_paddle_speed: float = config_dict["player_1_paddle_speed"]
        self.player_2_paddle_speed: float = config_dict["player_2_paddle_speed"]
        self.ball_initial_speed: float = config_dict["ball_initial_speed"]
        self.ball_acceleration_factor: float = config_dict["ball_acceleration_factor"]

        self.change_summary: str = config_dict["change_summary"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "player_1_paddle_width": self.player_1_paddle_width,
            "player_1_paddle_height": self.player_1_paddle_height,
            "player_2_paddle_width": self.player_2_paddle_width,
            "player_2_paddle_height": self.player_2_paddle_height,
            "ball_radius": self.ball_radius,
            "background_color": self._tuple_to_rgb(self.background_color),
            "ball_color": self._tuple_to_rgb(self.ball_color),
            "player_1_paddle_color": self._tuple_to_rgb(self.player_1_paddle_color),
            "player_2_paddle_color": self._tuple_to_rgb(self.player_2_paddle_color),
            "text_color": self._tuple_to_rgb(self.text_color),
            "text_background_color": self._tuple_to_rgb(self.text_background_color),
            "player_1_paddle_speed": self.player_1_paddle_speed,
            "player_2_paddle_speed": self.player_2_paddle_speed,
            "ball_initial_speed": self.ball_initial_speed,
            "ball_acceleration_factor": self.ball_acceleration_factor,
            "change_summary": self.change_summary,
        }

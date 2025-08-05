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
        self.paddle_width: int = config_dict["paddle_width"]
        self.paddle_height: int = config_dict["paddle_height"]
        self.ball_radius: int = config_dict["ball_radius"]

        self.background_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["background_color"])
        self.ball_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["ball_color"])
        self.paddle_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["paddle_color"])
        self.text_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["text_color"])
        self.text_background_color: pygame.color.Color = self._rgb_to_tuple(
            config_dict["text_background_color"])

        self.paddle_speed: float = config_dict["paddle_speed"]
        self.ball_initial_speed: float = config_dict["ball_initial_speed"]
        self.ball_acceleration_factor: float = config_dict["ball_acceleration_factor"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "paddle_width": self.paddle_width,
            "paddle_height": self.paddle_height,
            "ball_radius": self.ball_radius,
            "background_color": self._tuple_to_rgb(self.background_color),
            "ball_color": self._tuple_to_rgb(self.ball_color),
            "paddle_color": self._tuple_to_rgb(self.paddle_color),
            "text_color": self._tuple_to_rgb(self.text_color),
            "text_background_color": self._tuple_to_rgb(self.text_background_color),
            "paddle_speed": self.paddle_speed,
            "ball_initial_speed": self.ball_initial_speed,
            "ball_acceleration_factor": self.ball_acceleration_factor,
        }

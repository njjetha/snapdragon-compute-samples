# -----------------------------------------------------------------------------
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
#
# -----------------------------------------------------------------------------


import pygame
from typing_extensions import Annotated
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator, AfterValidator
from typing import Tuple


class RGBColor(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "title": "RGB Color",
        "description": "An RGB color that composes of the red, green, and blue components of a color."
    })

    red: int = Field(...,
                     description="The red component of the RGB color (0-255).", ge=0, le=255)
    green: int = Field(...,
                       description="The green component of the RGB color (0-255).", ge=0, le=255)
    blue: int = Field(...,
                      description="The blue component of the RGB color (0-255).", ge=0, le=255)

    def to_pygame_color(self) -> pygame.Color:
        return pygame.Color(self.red, self.green, self.blue)

    @classmethod
    def from_tuple(cls, rgb_tuple: Tuple[int, int, int]) -> 'RGBColor':
        return cls(red=rgb_tuple[0], green=rgb_tuple[1], blue=rgb_tuple[2])


def _rgb_to_pygame_color(v: RGBColor) -> pygame.Color:
    """Converts RGBColor Pydantic model to pygame.Color object."""
    return v.to_pygame_color()


def _pygame_color_to_rgb(v: pygame.Color) -> RGBColor:
    """Converts pygame.Color object to RGBColor Pydantic model."""
    return RGBColor(red=v.r, green=v.g, blue=v.b)


PygameColorType = Annotated[
    pygame.Color,
    BeforeValidator(_rgb_to_pygame_color),
    AfterValidator(_pygame_color_to_rgb)
]


class GameConfig(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "title": "Pong Game Configuration",
        "description": "Configuration settings for a classic Pong game, controlling paddle dimensions, ball and paddle physics, and colors."
    })

    # Dimensions
    player_1_paddle_width: int = Field(...,
                                       description="Width of Player 1's paddle.")
    player_1_paddle_height: int = Field(...,
                                        description="Height of Player 1's paddle.")
    player_2_paddle_width: int = Field(...,
                                       description="Width of Player 2's paddle.")
    player_2_paddle_height: int = Field(...,
                                        description="Height of Player 2's paddle.")
    ball_radius: int = Field(..., description="Radius of the game ball.")

    # Colors
    background_color: RGBColor = Field(...,
                                       description="Background color of the game.")
    ball_color: RGBColor = Field(..., description="Color of the game ball.")
    player_1_paddle_color: RGBColor = Field(...,
                                            description="Color of Player 1's paddle.")
    player_2_paddle_color: RGBColor = Field(...,
                                            description="Color of Player 2's paddle.")
    text_color: RGBColor = Field(...,
                                 description="Color of in-game text (e.g., scores).")
    text_background_color: RGBColor = Field(
        ..., description="Background color for text elements.")

    # Speeds and Dynamics
    player_1_paddle_speed: float = Field(...,
                                         description="Movement speed of Player 1's paddle.")
    player_2_paddle_speed: float = Field(...,
                                         description="Movement speed of Player 2's paddle.")
    ball_initial_speed: float = Field(...,
                                      description="Initial speed of the game ball.")
    ball_acceleration_factor: float = Field(
        ..., description="Factor by which ball speed increases after hits.")

    change_summary: str = Field(...,
                                description="A short and descriptive summary (less than 12 words) of changes made to this configuration compared to the last configuration.")

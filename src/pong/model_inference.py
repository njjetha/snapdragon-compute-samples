# -----------------------------------------------------------------------------
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
#
# -----------------------------------------------------------------------------


import openai
from foundry_local import FoundryLocalManager
from game_config import GameConfig
import json


# "Phi-3.5-mini-instruct-generic-cpu"  # "phi-4-mini-reasoning"
MODEL_NAME = "deepseek-r1-7b"


print("Loading Foundry Local model...")

manager = FoundryLocalManager(MODEL_NAME)

client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key  # API key is not required for local usage
)

required_list = [
    "player_1_paddle_width",
    "player_1_paddle_height",
    "player_2_paddle_width",
    "player_2_paddle_height",
    "ball_radius",
    "background_color",
    "ball_color",
    "player_1_paddle_color",
    "player_2_paddle_color",
    "text_color",
    "text_background_color",
    "player_1_paddle_speed",
    "player_2_paddle_speed",
    "ball_initial_speed",
    "ball_acceleration_factor",
    "change_summary",
]

color_description = {
    "type": "object",
    "properties": {
        "red": {
            "type": "number",
            "description": "A integer from 0 to 255 representing how bright the red component of this RGB color is",
        },
        "green": {
            "type": "number",
            "description": "A integer from 0 to 255 representing how bright the green component of this RGB color is",
        },
        "blue": {
            "type": "number",
            "description": "A integer from 0 to 255 representing how bright the blue component of this RGB color is",
        },
    },
    "required": ["red", "green", "blue"],
    "additionalProperties": False,
}

json_scheme = {
    "type": "object",
    "properties": {
        "player_1_paddle_width": {
            "type": "number",
            "description": "The width of the player 1's paddle"
        },
        "player_1_paddle_height": {
            "type": "number",
            "description": "The height of the player 1's paddle"
        },
        "player_2_paddle_width": {
            "type": "number",
            "description": "The width of the player 2's paddle"
        },
        "player_2_paddle_height": {
            "type": "number",
            "description": "The height of the player 2's paddle"
        },
        "ball_radius": {
            "type": "number",
            "description": "The radius of the ball in the game"
        },
        "background_color": color_description,
        "ball_color": color_description,
        "player_1_paddle_color": color_description,
        "player_2_paddle_color": color_description,
        "text_color": color_description,
        "text_background_color": color_description,
        "player_1_paddle_speed": {
            "type": "number",
            "description": "The speed of the player 1's paddle"
        },
        "player_2_paddle_speed": {
            "type": "number",
            "description": "The speed of the player 2's paddle"
        },
        "ball_initial_speed": {
            "type": "number",
            "description": "The initial speed of the ball in the game"
        },
        "ball_acceleration_factor": {
            "type": "number",
            "description": "The rate the ball in the game accelerates by"
        },
        "change_summary": {
            "type": "string",
            "description": "A short sentence explaining the changes from the previous game configuration and the current new game configuration. Make sure the sentence is less than 12 words."
        },
    },
    "required": required_list,
    "additionalProperties": False
}


def generate_game_config(user_prompt: str, last_scored_player: int, previous_config: GameConfig) -> GameConfig:
    max_retries = 25
    retry_count = 0

    error = None

    ai_prompt = f"""
    <goal>
    Generate a new configuration for the Pong game using the provided player {last_scored_player} prompt, "{user_prompt}", and context. The configuration must comply with the json_schema.
    </goal>

    <instructions>
    - Use the following prompt from player {last_scored_player} to change the game configuration: "{user_prompt}".
    - Return ONLY a valid JSON object that matches the schema outlined below.
    - The JSON must include ALL of the following required keys and no others:
    {', '.join(required_list)}.
    - Do NOT include any notes, explanations, or extra properties.
    - Do NOT change anything in the game configuration that is not being addressed in the player {last_scored_player} prompt, "{user_prompt}".
    - Only change what is needed from the previous configuration:
    {json.dumps(previous_config.to_dict())}.
    {f"- Avoid errors similar to the last configuration issue: {error}" if error is not None else ""}
    </instructions>

    <json_scheme>
    {json_scheme}
    </json_scheme>

    <output_contract>
    - Output MUST be a single JSON object.
    - Output MUST start with "{" and end with "}".
    - Do NOT include any prose, comments, code fences, or explanations.
    - Do NOT include markdown, backticks, or surrounding text.
    - Use ONLY double-quoted keys and string values.
    - No trailing commas, NaN, Infinity, undefined, or comments.
    - All numeric values must be valid JSON numbers (integers or decimals).
    </output_contract>

    <output>
    Respond ONLY with the valid JSON object containing all required properties. Use the following prompt from player {last_scored_player} to change the game configuration: "{user_prompt}".
    </output>
    """

    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model=manager.get_model_info(MODEL_NAME).id,
                messages=[{
                    "role": "user",
                    "content": ai_prompt
                }],
                temperature=min(1, 0.00001 + (0.15 * retry_count)),
                max_tokens=4096,
            )

            error = None

            result = response.choices[0].message.content.lower()

            # Remove think tag
            think_tag = "</think>"

            if think_tag in result:
                end_index = result.index(think_tag) + len(think_tag)
                cleaned_result = result[end_index + 1:].strip()
            else:
                cleaned_result = result.strip()

            # Remove any unneeded formatting
            cleaned_result = cleaned_result.replace(
                '```', '').replace('json', '').replace('<response>', '').replace('functools', '')

            cleaned_result_json: dict = json.loads(cleaned_result)

            # If needed add missing keys
            previous_config_dict = previous_config.to_dict()
            prev_keys = set(previous_config_dict.keys())
            missing_keys = prev_keys - set(cleaned_result_json.keys())

            for key in missing_keys:
                cleaned_result_json[key] = previous_config_dict[key]

            return GameConfig(cleaned_result_json)

        except json.JSONDecodeError as e:
            error = f"JSONDecodeError: Failed to parse JSON from model response. Error: {e}\nContent that caused the error: '{cleaned_result}'"

            retry_count += 1

        except Exception as e:
            print(
                f"An unexpected error occurred: {e}")

            retry_count += 1

    raise ValueError(
        f"Failed to obtain a valid game configuration from the model after {max_retries} retries")

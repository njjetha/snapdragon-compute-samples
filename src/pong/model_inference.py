import openai
from foundry_local import FoundryLocalManager
from game_config import GameConfig
import json

from pprint import pprint

MODEL_NAME = "phi-3.5-mini"  # "deepseek-r1-7b"


manager = FoundryLocalManager(MODEL_NAME)

client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key  # API key is not required for local usage
)

required_list = [
    "paddle_width",
    "paddle_height",
    "ball_radius",
    "background_color",
    "ball_color",
    "paddle_color",
    "text_color",
    "text_background_color",
    "paddle_speed",
    "ball_initial_speed",
    "ball_acceleration_factor"
]

rgb_descriptions = {
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
}

tools = [{
    "type": "function",
    "name": "configure_pygame_pong_game",
    "description": "Configures a game of pong based off of the parameters",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "paddle_width": {
                "type": "number",
                "description": "The width of the players' paddles"
            },
            "paddle_height": {
                "type": "number",
                "description": "The height of the players' paddles"
            },
            "ball_radius": {
                "type": "number",
                "description": "The radius of the ball in the game"
            },
            "background_color": {
                "type": "object",
                "properties": rgb_descriptions,
                "required": ["red", "green", "blue"]
            },
            "ball_color": {
                "type": "object",
                "properties": rgb_descriptions,
                "required": ["red", "green", "blue"]
            },
            "paddle_color": {
                "type": "object",
                "properties": rgb_descriptions,
                "required": ["red", "green", "blue"]
            },
            "text_color": {
                "type": "object",
                "properties": rgb_descriptions,
                "required": ["red", "green", "blue"]
            },
            "text_background_color": {
                "type": "object",
                "properties": rgb_descriptions,
                "required": ["red", "green", "blue"]
            },
            "paddle_speed": {
                "type": "number",
                "description": "The speed of the players' paddles"
            },
            "ball_initial_speed": {
                "type": "number",
                "description": "The initial speed of the ball in the game"
            },
            "ball_acceleration_factor": {
                "type": "number",
                "description": "The rate the ball in the game accelerates by"
            },
        },
        "required": required_list,
        "additionalProperties": False
    }
}]


def generate_game_config(prompt: str, previous_config: GameConfig) -> GameConfig:
    max_retries = 25
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model=manager.get_model_info(MODEL_NAME).id,
                messages=[{
                    "role": "user",
                    "content": f"What should the new configuration of the game of pong be based on the prompt: {prompt}. Only send back all of the arguments for the tool in a valid JSON format. Make sure the following keys are in the JSON, {', '.join(required_list)}. DO NOT respond with any notes or explanations, only respond with the valid JSON. Make sure the new configuration is not the same as the previous game configuration. The previous game configuration was {json.dumps(previous_config.to_dict())}"
                }],
                max_completion_tokens=1024,
                tools=tools,
            )

            result = response.choices[0].message.content

            result = result.lower()

            # remove think tag
            think_tag = "</think>"

            if think_tag in result:
                end_index = result.index(think_tag) + len(think_tag)
                cleaned_result = result[end_index + 1:].strip()
            else:
                cleaned_result = result.strip()

            # remove any formatting
            cleaned_result = cleaned_result.replace(
                '```', '').replace('json', '')

            cleaned_result_json = json.loads(cleaned_result)

            pprint(cleaned_result_json)

            return GameConfig(cleaned_result_json)

        except json.JSONDecodeError as e:
            print(
                f"JSONDecodeError: Failed to parse JSON from model response. Error: {e}")
            print(f"Content that caused the error: '{cleaned_result}'")

            retry_count += 1
        except Exception as e:
            print(
                f"An unexpected error occurred during API call or processing: {e}")

            retry_count += 1

        raise ValueError(
            f"Failed to obtain a valid game configuration from the model after {max_retries} retries")

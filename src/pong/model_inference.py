import openai
from foundry_local import FoundryLocalManager
from game_config import GameConfig
import json

MODEL_NAME = 'deepseek-r1-7b'


manager = FoundryLocalManager(MODEL_NAME)

client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key  # API key is not required for local usage
)


rgb_descriptions = {
    "red": {
        "type": "number",
        "description": "A integer from 0 to 255 representing how bright the red component of this color is",
    },
    "green": {
        "type": "number",
        "description": "A integer from 0 to 255 representing how bright the green component of this color is",
    },
    "blue": {
        "type": "number",
        "description": "A integer from 0 to 255 representing how bright the blue component of this color is",
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
        "required": [
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
        ],
        "additionalProperties": False
    }
}]


def generate_game_config(previous_config: GameConfig) -> dict:
    response = client.chat.completions.create(
        model=manager.get_model_info(MODEL_NAME).id,
        messages=[{
            "role": "user",
            "content": f"What should the configuration of the game of pong be? Only send back the arguments for the tool in a JSON format. The previous game configuration was {json.dumps(previous_config.to_dict())}"
        }],
        max_completion_tokens=1024,
        tools=tools,
    )

    result = response.choices[0].message.content

    # remove think tag
    think_tag = "</think>"

    end_index = result.lower().index(think_tag) + len(think_tag)
    cleaned_result = result[end_index + 1:].strip()

    # remove any formatting
    cleaned_result = cleaned_result.replace('```', '').replace('json', '')

    print(cleaned_result)

    return GameConfig(json.loads(cleaned_result))

# -----------------------------------------------------------------------------
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause
#
# -----------------------------------------------------------------------------


from ollama import chat
from game_config import GameConfig
from pydantic import ValidationError


MODEL_NAME: str = "gemma3:4b-it-qat"


print("Loading Ollama model...")


def generate_game_config(user_prompt: str, last_scored_player: int, previous_config: GameConfig) -> GameConfig:
    max_retries: int = 25
    retry_count: int = 0

    error: str | None = None

    ai_prompt = f"""
    <goal>
    Generate a new configuration for the Pong game using the provided player {last_scored_player} prompt, "{user_prompt}", and context.
    </goal>

    <instructions>
    - Use the following prompt from player {last_scored_player} to change the game configuration: "{user_prompt}".
    - Do NOT change anything in the game configuration that is not being addressed in the player {last_scored_player} prompt, "{user_prompt}".
    - Do NOT change any colors unless asked to by the player's prompt.
    - Do NOT send back the previous configuration without changing the configuration according to the player's prompt.
    - ONLY change what is needed from the previous configuration:
    {previous_config.model_dump_json()}.
    {f"- Avoid errors similar to the last configuration issue: {error}" if error is not None else ""}
    </instructions>

    <output>
    Respond ONLY with the valid GameConfig object containing all required properties. Use the following prompt from player {last_scored_player} to change the game configuration: "{user_prompt}".
    </output>
    """

    while retry_count < max_retries:
        try:
            response = chat(
                messages=[
                    {
                        "role": "user",
                        "content": ai_prompt,
                    }
                ],
                model=MODEL_NAME,
                options={
                    "temperature": min(1, 0.00001 + (0.15 * retry_count)),
                    "num_ctx": 4096,
                    "repeat_penalty": 1.1,
                },
                format=GameConfig.model_json_schema(),
            )

            result = response.message.content

            print("Try #", retry_count)

            print(result)

            error = None

            return GameConfig.model_validate_json(result)

        except ValidationError as e:
            error = f"ValidationError: Failed to validate GameConfig object. Error: {e}\nContent that caused the error: {result}'"

            retry_count += 1

        except Exception as e:
            print(
                f"An unexpected error occurred: {e}")

            retry_count += 1

    raise ValueError(
        f"Failed to obtain a valid game configuration from the model after {max_retries} retries")

# 🕹️ Prompt Pong

This interactive two-player game of pong showcases the on-device inferencing capabilities of the Snapdragon X Elite platform and Microsoft Foundry Local. Players compete and the round's winner can dynamically alter the game environment by prompting an on-device large language model (LLM). This real-time sample demonstrates how local AI processing can enable adaptive gameplay, personalized experiences, and low-latency decision-making all without relying on cloud connectivity.


## Requirements
### Hardware
1. A device with a Qualcomm [Snapdragon X Elite Processor](https://www.qualcomm.com/products/mobile/snapdragon/laptops-and-tablets/snapdragon-x-elite) (or QNN compatible NPU)


### Software

1. [Python 3.13](https://www.python.org/)
2. [Microsoft Foundry Local](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)
3. [Qualcomm® Neural Processing SDK](https://www.qualcomm.com/developer/software/neural-processing-sdk-for-ai)


## Installation Instructions

1. Clone this Github Repository directly on your Snapdragon X Elite device
    - Use a command such as `git clone https://github.com/qualcomm/snapdragon-compute-samples.git`
2. Install Microsoft Foundry local
    - Follow these [instructions](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/get-started)
3. Install Qualcomm® Neural Processing SDK
    - You can find the SDK on the [Qualcomm Software Center](https://softwarecenter.qualcomm.com/)
4. Install the required Python packages
    - Run the command `pip install -r requirements.txt`
    - Make sure you are in the `src/pong` directory


## Usage

1. Make sure you have first followed the [Requirements](#requirements) and [Installation Instructions](#installation-instructions) steps above
2. Start the game of pong with the command: `python main.py`
    - Make sure you are in the `src/pong` directory
3. Controls:
    - Player 1 (left paddle): 'W' for up and 'S' for down
    - Player 2 (right paddle): 'Up Arrow' for up and 'Down Arrow' for down
4. After a point is scored, the winner of the round is asked to provide a prompt to change the game. An on-device LLM will re-generate the Pong game based on the prompt. After 5 points, the game will end!

<details>
    <summary>Technical Details</summary>
    <h3>Tech Stack Overview</h3>
    <p>Prompt Pong is completely designed in Python. The main Python packages used are:</p>
    <ul>
        <li><a href="https://www.pygame.org/docs/" target="_blank">pygame</a>: a package for Python game development</li>
        <li><a href="https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/how-to/how-to-integrate-with-inference-sdks?pivots=programming-language-python" target="_blank">foundry_local</a>: a package that interfaces with Microsoft's Foundry Local SDK</li>
        <li><a href="https://github.com/openai/openai-python" target="_blank">openai</a>: a package integrated with  foundry_local models to simplify model inferencing</li>
    </ul>
    <p>The game is composed of three Python files:</p>
    <ul>
        <li><a href="./main.py" target="_blank">main.py</a>: contains the main game loop and game logic</li>
        <li><a href="./model_inference.py" target="_blank">model_inference.py</a>: contains the actual inferencing of the on-device models</li>
        <li><a href="./game_config.py" target="_blank">game_config.py</a>: contains a class that configures the Pong game</li>
    </ul>
    <h3>Model Inferencing</h3>
    <img src="./images/prompt_pong_model_sequence.png" style="min-width: 480px; max-width: 65%; height: auto;"/>
    <p>Between points being scored, the winner of that round is asked to provide a prompt to change the game. Once the player sends a prompt, the prompt and previous game configuration are sent to a Foundry Local model on a separate thread. Once the model returns the new game configuration, the game loop and game logic are re-rendered and the game continues until 5 points are scored.</p>
    <h4>System Prompt Methodology</h4>
    <p>When designing the prompt for the Foundry Local model, it was important to first understand the <a href="https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/reference/reference-rest" target="_blank">constraints and parameters</a>. A low temperature and set max_tokens were used to ensure consistent and accurate results. To enure that the model properly returns the structured data needed, several additional checks were added. The final prompt was created based on system prompts of other popular ai tools.</p>
</details>


## License

This repository and project is licensed under the [BSD-3-clause License](https://spdx.org/licenses/BSD-3-Clause.html).

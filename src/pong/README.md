# 🕹️ Prompt Pong

This interactive two-player game of pong showcases the on-device inferencing capabilities of the Snapdragon X Elite platform. Players compete and the round's winner can dynamically alter the game environment by prompting an on-device large language model (LLM). This real-time sample demonstrates how local AI processing can enable adaptive gameplay, personalized experiences, and low-latency decision-making all without relying on cloud connectivity.


## Requirements
### Hardware
1. A device with a Qualcomm [Snapdragon X Elite Processor](https://www.qualcomm.com/products/mobile/snapdragon/laptops-and-tablets/snapdragon-x-elite) (or QNN compatible NPU)


### Software

1. [Python 3.13](https://www.python.org/)
2. [Microsoft Foundry Local](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/)
3. [Qualcomm® Neural Processing SDK](https://www.qualcomm.com/developer/software/neural-processing-sdk-for-ai)


## Installation Instructions

1. Clone this Github Repository directly on your Snapdragon X Elite device
    - Use a command such as `git clone REPlACE-ME`
2. Install Microsoft Foundry local
    - Follow the following [instructions](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/get-started)
3. Install Qualcomm® Neural Processing SDK
    - You can find the SDK on the [Qualcomm Software Center](https://softwarecenter.qualcomm.com/)


## Usage

1. Make sure you have first followed the [Requirements](#requirements) and [Installation Instructions](#installation-instructions) steps above
2. Start the game of pong with the command: `python main.py`
    - Make sure you are in the `src/pong` directory
3. The player controls are as follows:
    - Player 1: 'W' for up and 'S' for down
    - Player 2: 'Up Arrow' for up and 'Down Arrow' for down

<details>
    <summary>Technical Details</summary>
    <p>...</p>
</details>


## License

This repository and project is licensed under the [BSD-3-clause License](https://spdx.org/licenses/BSD-3-Clause.html).

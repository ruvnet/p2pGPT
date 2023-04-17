# P2P GPT for Slack and Web Sockets Add-on

This project is an add-on for AutoGPT, an experimental open-source application that showcases the capabilities of the GPT-4 language model. AutoGPT, driven by GPT-4, chains together LLM "thoughts" to autonomously achieve user-defined goals. As one of the first examples of GPT-4 running fully autonomously, AutoGPT pushes the boundaries of what is possible with AI.

The P2P GPT for Slack and Web Sockets Output add-on extends AutoGPT's functionality by enabling it to run in a P2P network using websockets. This allows for seamless communication and interaction with the GPT-4 model through popular messaging platforms like Slack, as well as custom web applications that leverage WebSockets for real-time communication.

By integrating AutoGPT into a P2P network, this add-on opens up new possibilities for distributed AI applications. Users can collaborate and share resources in real-time, making it easier than ever to harness the power of GPT-4 for various tasks, including natural language processing, data analysis, and content generation.

Whether you're an AI enthusiast, a developer looking to explore the potential of GPT-4, or a business seeking to leverage AI-driven solutions, the P2P GPT for Slack and Web Sockets Output add-on offers a powerful and flexible way to tap into the incredible capabilities of AutoGPT in a P2P environment.

## Prerequisites

- Python 3.6 or higher
- Git (for cloning the repository)
- pip (for installing dependencies)

## Installation 

1. Clone this repository:
git clone https://github.com/ruvnet/P2PGPT.git

2. Run the setup_autogpt.sh script
chmod +x setup_autogpt.sh

3. Now, run the setup_autogpt.sh script to set up AutoGPT and its dependencies:

./setup_autogpt.sh

4. Verify the installation
After the script completes, verify that AutoGPT has been installed correctly by running the following command:
python -m autogpt --help

## Getting Started

### Create a Slack bot

First, you need to create a Slack bot and obtain the necessary API token. Follow the instructions in the official Slack documentation to create a new bot and install it to your workspace.

### Obtain the Slack API token

After creating the bot, go to the "OAuth & Permissions" tab in your bot settings. Under the "Bot Token Scopes" section, make sure you have the following scopes added:

- `channels:history`
- `chat:write`
- `chat:write.public`

Scroll up to the "Tokens for Your Workspace" section and copy the "Bot User OAuth Token". It should start with `xoxb-`.

### Set the environment variables

In your terminal or environment file (e.g., .env), set the SLACK_CHANNEL_ID and SLACK_API_TOKEN environment variables:

```
export SLACK_CHANNEL_ID="your_channel_id_here"
export SLACK_API_TOKEN="your_slack_api_token"
```
Replace your_channel_id_here with the desired Slack channel ID and your_slack_api_token with the token you obtained earlier.

If you are using a .env file or similar to manage environment variables, add the following lines:

```
SLACK_CHANNEL_ID=your_channel_id_here
SLACK_API_TOKEN=your_slack_api_token
```
1. Navigate to the cloned repository:
cd P2PGPT

2. Install the required dependencies:
pip install -r requirements.txt

## Configuration

1. Set up a Slack API token by creating a new bot and adding it to your desired channel.
2. Set the `SLACK_ENDPOINT` environment variable with your Slack API token:
export SLACK_ENDPOINT=your_slack_api_token

## Usage

1. Make the `startup.sh` script executable:
chmod +x startup.sh

2. Start the application by running the `startup.sh` script:
./startup.sh

3. Open your web browser and navigate to `http://localhost:8080` to interact with the GPT model using the Web Sockets interface.
4. Send messages in the configured Slack channel to interact with the GPT model using Slack.

## startup.sh

The `startup.sh` script is responsible for starting both the FastAPI app and the CLI script. Here's the content of the `startup.sh` file:

```bash
#!/bin/bash

# Run the FastAPI app in the background
uvicorn main:app --host 0.0.0.0 --port 8080 &

# Run the CLI script in /scripts/main.py in the foreground
# python -m autogpt --continuous
# python autogpt --use-memory pinecone

# Wait for all background processes to complete
wait

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

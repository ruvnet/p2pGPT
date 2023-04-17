from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from typing import List, Optional, Dict
from pydantic import BaseModel
import subprocess
import threading
import asyncio
from fastapi.responses import JSONResponse
from collections import deque
import concurrent.futures  # Import the concurrent.futures module
import os
import subprocess
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = FastAPI()
cli_process = None

# slack_endpoint = os.environ["SLACK_ENDPOINT"]
slack_api_token = os.environ.get("SLACK_API_TOKEN", "")

def send_message_to_slack_channel(message):
    channel_id = os.environ.get("SLACK_CHANNEL_ID", "")
    if slack_api_token and channel_id:
        try:
            slack_client = WebClient(token=slack_api_token)
            response = slack_client.chat_postMessage(channel=channel_id, text=message)
        except SlackApiError as e:
            print(f"Error sending message to Slack channel: {e}")

# Define a model for bot registration
class BotRegistration(BaseModel):
    bot_id: str
    job_description: str
    role: str
    responsibilities: List[str]

# Define a model for task allocation
class TaskAllocation(BaseModel):
    task_id: str
    task_description: str

registered_bots: Dict[str, BotRegistration] = {}
task_queue: deque = deque()
current_bot_index = 0

# List to store registered bots
registered_bots: Dict[str, BotRegistration] = {}

# Define a dictionary to store cached responses
cached_responses: Dict[str, str] = {}

# Create a process pool executor for parallel execution
executor = concurrent.futures.ProcessPoolExecutor()

@app.on_event("startup")
async def startup_event():
    global cli_process
    # Start the CLI script as a subprocess
    cli_process = subprocess.Popen(
        ["python", "-m", "autogpt", "--continuous"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>CLI Interaction</title>
    </head>
    <body>
        <h1>CLI Interaction</h1>
        <textarea id="output" rows="10" cols="50"></textarea><br>
        <input type="text" id="input" autocomplete="off"/>
        <button onclick="sendMessage()">Send</button>
        <script>
            var ws = new WebSocket("wss://autogpt-ruv-editon.ruvnet.repl.co/ws");
            ws.onmessage = function(event) {
                document.querySelector("#output").value += event.data + '\\n';
            };
            function sendMessage() {
                var input = document.querySelector("#input").value;
                ws.send(input);
                document.querySelector("#input").value = "";
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get("/execute-command/{command}")
async def execute_command(request: Request, command: str):
    global cli_process
    # Send the command to the CLI script's stdin
    print(command, file=cli_process.stdin, flush=True)
    # Define a buffer to store the response
    response_buffer = []
    while True:
        # Read one line at a time from the CLI script's stdout
        output = cli_process.stdout.readline().strip()
        # Filter out "Thinking..." messages
        if "Thinking..." not in output:
            response_buffer.append(output)
        # Break the loop when the CLI script stops sending output
        if not output:
            break
    # Join the response_buffer into a single string
    response_text = "\n".join(response_buffer)
    # Return the response as a JSON object
    return JSONResponse(content={"result": response_text})

# Define a request model for the input data
class InputData(BaseModel):
    input_text: str

# Define a response model for the AI model's response
class AIResponse(BaseModel):
    response_text: str

@app.post("/execute-command-json/", response_model=AIResponse)
async def execute_command_json(input_data: InputData) -> AIResponse:
    # Get input_text from the request body
    input_text = input_data.input_text
    
    # Use the main function from the script to process the input
    # and get the AI model's response (replace with the actual function)
    response_text = main(input_text)
    
    # Return the AI model's response as a JSON object
    return AIResponse(response_text=response_text)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global cli_process
    await websocket.accept()
    # Get the running event loop
    loop = asyncio.get_running_loop()
    # Start the thread to read CLI output
    threading.Thread(target=read_cli_output, args=(websocket, loop), daemon=True).start()
    try:
        while True:
            # Receive input from the WebSocket
            data = await websocket.receive_text()
            # Send the command to the CLI script's stdin
            print(data, file=cli_process.stdin, flush=True)
    except WebSocketDisconnect as e:
        # Handle the WebSocketDisconnect exception
        print(f"WebSocket disconnected with code: {e.code}")

def read_cli_output(websocket: WebSocket, loop: asyncio.AbstractEventLoop):
    global cli_process
    buffer = ""  # Buffer to store characters until a newline is encountered
    while True:
        # Read one character at a time from the CLI script's stdout
        char = cli_process.stdout.read(1)
        if char == '\n':
            # Check if the buffered content contains "Thinking..."
            if "Thinking..." not in buffer:
                # Send the buffered content when a newline is encountered
                asyncio.run_coroutine_threadsafe(websocket.send_text(buffer), loop)
                # Send the buffered content to the Slack channel
                send_message_to_slack_channel(slack_channel_id, buffer)
            buffer = ""  # Reset the buffer
        elif char != '\b':
            # Append non-backspace characters to the buffer
            buffer += char

@app.post("/register-bot/")
async def register_bot(bot_registration: BotRegistration):
    # Check if the bot is already registered
    if bot_registration.bot_id in registered_bots:
        raise HTTPException(status_code=400, detail="Bot is already registered.")
    
    # Register the bot and add it to the list of registered bots
    registered_bots[bot_registration.bot_id] = bot_registration
    
    # Return a success message
    return {"message": "Bot registration successful"}

# Define a function that runs both main.py and scripts/main.py
def run_scripts(task_description: str) -> str:
    # Define the path to the Auto-GPT directory
    auto_gpt_dir = os.path.join(os.path.dirname(__file__), "Auto-GPT")
    
    # Define the paths to the scripts
    main_script_path = os.path.join(auto_gpt_dir, "main.py")
    scripts_main_script_path = os.path.join(auto_gpt_dir, "scripts", "main.py")
    
    # Start the main.py script as a subprocess
    main_process = subprocess.Popen(
        ["python", main_script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )
    
    # Start the scripts/main.py script as a subprocess
    scripts_main_process = subprocess.Popen(
        ["python", scripts_main_script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )
    
    # Process the task description and get the AI model's response
    # (You can replace this part with the actual implementation)
    response = f"Hello, {task_description}!"
    
    # Terminate the subprocesses (if needed)
    main_process.terminate()
    scripts_main_process.terminate()
    
    return response

@app.post("/allocate-task/")
async def allocate_task(task: TaskAllocation):
    global current_bot_index
    
    # Check if the response for the task description is cached
    if task.task_description in cached_responses:
        # Return the cached response
        return {"response": cached_responses[task.task_description]}
    
    # Add the task to the task queue
    task_queue.append(task)
    
    # Get the list of registered bots
    bot_ids = list(registered_bots.keys())
    
    # If no bots are registered, return an error message
    if not bot_ids:
        raise HTTPException(status_code=400, detail="No bots are registered.")
    
    # Allocate the task to the next bot in the list (round-robin approach)
    allocated_bot_id = bot_ids[current_bot_index]
    
    # Update the current_bot_index for the next allocation
    current_bot_index = (current_bot_index + 1) % len(bot_ids)
    
    # Submit the task to the process pool for parallel execution
    future = executor.submit(run_scripts, task.task_description)
    
    # Wait for the result and retrieve the response
    response = future.result()
    
    # Cache the response
    cached_responses[task.task_description] = response
    
    # Return the allocated bot's ID and the response
    return {"allocated_bot_id": allocated_bot_id, "response": response}

# Define a function to compute the response (replace with the actual implementation)
def compute_response(task_description: str) -> str:
    # Process the task description and get the AI model's response
    # ...
    response = f"Hello, {task_description}!"
    return response


# Define the main function that interacts with the AI model
# (replace with the actual implementation)
def main(input: str) -> str:
    # Process the input and get the AI model's response
    # ...
    response = f"Hello, {input}!"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

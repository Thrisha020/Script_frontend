"""import os
import subprocess
import shutil
import argparse
from datetime import datetime
import json
from dataclasses import dataclass, field
from typing import List
from adalflow.core.types import (
    Conversation,
)

from adalflow.core.db import LocalDB
from adalflow.core.component import Component

# Memory management class to store conversation history
class Memory:
    def __init__(self, memory_file):
        self.memory_file = memory_file
        self.memory = self.load_memory()

    def load_memory(self):
        Load memory from the file.
        try:
            with open(self.memory_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_memory(self):
        Save memory to the file.
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=4)

    def log_turn(self, user_message, assistant_message):
    Log a conversation turn with a timestamp.
        turn = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_message,
            "assistant": assistant_message
        }
        self.memory.append(turn)
        self.save_memory()

    def retrieve_memory(self):
     
        return self.memory

# Log file path
LOG_FILE = "internet_connection_log.txt"

# Function to log messages to the file and also to the memory
def log_to_file_and_memory(message, log_file, memory):
  
    with open(log_file, "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - {message}\n"
        file.write(log_message)
        file.write("-" * 40 + "\n")  # Separator for readability
        print(log_message)  # Print the message to the terminal
    memory.log_turn(message, message)  # Store the message in the memory

def clone_repo(repo_url, clone_path, log_file, memory):

    try:
        subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
        message = f"Repository cloned successfully to {clone_path}."
        log_to_file_and_memory(message, log_file, memory)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error cloning repository: {e}"
        log_to_file_and_memory(message, log_file, memory)
        return message

def is_git_repo(folder_path):

    return os.path.isdir(os.path.join(folder_path, ".git"))

def pull_latest_changes(repo_path, log_file, memory):

    try:
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
        message = f"Latest changes pulled successfully."
        log_to_file_and_memory(message, log_file, memory)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error pulling latest changes: {e}"
        log_to_file_and_memory(message, log_file, memory)
        return message

def delete_folder(folder_path, log_file, memory):

    permission = input(f"The folder '{folder_path}' is not a git repository. Do you want to delete it? (yes/no): ").lower()
    if permission == 'yes':
        shutil.rmtree(folder_path)
        message = f"Folder '{folder_path}' deleted."
        log_to_file_and_memory(message, log_file, memory)
        return True
    else:
        message = f"Operation canceled for folder '{folder_path}'."
        log_to_file_and_memory(message, log_file, memory)
        return False

def main(repo_name, base_url, active_path):
    log_file = f"{active_path}/internet_connection_log.txt"
    memory = Memory("session_memory.json")  # Initialize memory to store conversation history
    
    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(active_path, repo_name)

    # Clone if the folder does not exist
    if not os.path.isdir(clone_path):
        log_to_file_and_memory(f"Cloning repository from {repo_url} to {clone_path}...", log_file, memory)
        return clone_repo(repo_url, clone_path, log_file, memory)
    
    # If it's a git repository, pull latest changes
    if is_git_repo(clone_path):
        log_to_file_and_memory(f"Repository already cloned at {clone_path}. Pulling latest changes...", log_file, memory)
        return pull_latest_changes(clone_path, log_file, memory)
    else:
        # Ask for permission to delete the folder and re-clone
        log_to_file_and_memory(f"Folder '{clone_path}' exists but is not a git repository.", log_file, memory)
        if delete_folder(clone_path, log_file, memory):
            log_to_file_and_memory(f"Re-cloning repository from {repo_url} to {clone_path}...", log_file, memory)
            return clone_repo(repo_url, clone_path, log_file, memory)
        else:
            return "Operation canceled."

# Command-line interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process repository name and base URL.")
    
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    parser.add_argument("active_path", type=str, help="It will download in the current path")
    
    args = parser.parse_args()
    
    result = main(args.repo_name, args.base_url, args.active_path)
    
    # Retrieve and print conversation history
    memory = Memory("session_memory.json")
    history = memory.retrieve_memory()
    print("\nConversation History:")
    for turn in history:
        print(f"{turn['timestamp']} - User: {turn['user']}, Assistant: {turn['assistant']}")
"""

import os
import subprocess
import shutil
import argparse
import json
from datetime import datetime
from adalflow.core.db import LocalDB
from adalflow.core.types import DialogTurn, UserQuery, AssistantResponse
from adalflow.core.component import Component

# Define the Memory class to store conversation history

class Memory(Component):
    def __init__(self, turn_db: LocalDB = None):
        super().__init__()
        self.current_conversation = []  # Store conversation as list of DialogTurn objects
        self.turn_db = turn_db or LocalDB()

    def store_turn(self, user_input: str, assistant_response: str):
        user_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        assistant_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        dialog_turn = DialogTurn(
            user_query=UserQuery(query_str=user_input),
            assistant_response=AssistantResponse(response_str=assistant_response),
            user_query_timestamp=user_time,
            assistant_response_timestamp=assistant_time,
        )
        
        self.current_conversation.append(dialog_turn)
        self.turn_db.save(dialog_turn)

    def get_conversation_history(self):
        return self.current_conversation

    def save_conversation(self):
        # Save the current conversation to the DB
        self.turn_db.save(self.current_conversation)
        self.current_conversation = []  # Reset the conversation for the new session


# Function to log messages to a file and print to terminal

def log_to_memory(message, LOG_FILE, user_input=None):
    """Logs a message and stores the conversation."""
    if user_input:
        memory.store_turn(user_input, message)  # Store user-assistant interaction
    else:
        memory.store_turn('System', message)  # System actions stored as a conversation

    # Log to the file (same as your original logging)
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - {message}\n"
        log_file.write(log_message)
        log_file.write("-" * 40 + "\n")  # Separator for readability
        print(log_message)  # Print the message to the terminal


# Function to clone the repository

def clone_repo(repo_url, clone_path, LOG_FILE, user_input=None):
    try:
        subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
        message = f"Repository cloned successfully to {clone_path}."
        log_to_memory(message, LOG_FILE, user_input)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error cloning repository: {e}"
        log_to_memory(message, LOG_FILE, user_input)
        return message


# Function to check if a folder is a git repository

def is_git_repo(folder_path):
    return os.path.isdir(os.path.join(folder_path, ".git"))


# Function to pull the latest changes from the repository

def pull_latest_changes(repo_path, LOG_FILE, user_input=None):
    try:
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
        message = f"Latest changes pulled successfully."
        log_to_memory(message, LOG_FILE, user_input)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error pulling latest changes: {e}"
        log_to_memory(message, LOG_FILE, user_input)
        return message


# Function to delete a folder (if it's not a git repository)

def delete_folder(folder_path, LOG_FILE, user_input=None):
    permission = input(f"The folder '{folder_path}' is not a git repository. Do you want to delete it? (yes/no): ").lower()
    if permission == 'yes':
        shutil.rmtree(folder_path)
        log_to_memory(f"Folder '{folder_path}' deleted.", LOG_FILE, user_input)
        return True
    else:
        log_to_memory(f"Operation canceled for folder '{folder_path}'.", LOG_FILE, user_input)
        return False


# Main function to handle repository cloning and pulling

def main(repo_name, base_url, active_path, user_input=None):
    LOG_FILE = f"{active_path}/internet_connection_log.txt"
    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(active_path, repo_name)

    # Clone if the folder does not exist
    if not os.path.isdir(clone_path):
        message = clone_repo(repo_url, clone_path, LOG_FILE, user_input)
        return message
    
    # If it's a git repository, pull latest changes
    if is_git_repo(clone_path):
        message = pull_latest_changes(clone_path, LOG_FILE, user_input)
        return message
    else:
        # Ask for permission to delete the folder and re-clone
        if delete_folder(clone_path, LOG_FILE, user_input):
            message = clone_repo(repo_url, clone_path, LOG_FILE, user_input)
            return message
        else:
            message = "Operation canceled."
            log_to_memory(message, LOG_FILE, user_input)
            return message


# Function to print the conversation history

def print_conversation_history():
    history = memory.get_conversation_history()
    for turn in history:
        print(f"User: {turn.user_query.query_str}")
        print(f"Assistant: {turn.assistant_response.response_str}")
        print(f"User Timestamp: {turn.user_query_timestamp}")
        print(f"Assistant Timestamp: {turn.assistant_response_timestamp}")


# LocalDB Class with Save Method

class LocalDB:
    def __init__(self, db_file='conversation_db.json'):
        self.db_file = db_file
        self.load_data()

    def load_data(self):
        """Load existing data from the file (if any)."""
        try:
            with open(self.db_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    self.data = []  # If empty, initialize an empty list
                else:
                    self.data = json.loads(content)
                    # Convert dictionaries back to DialogTurn objects
                    self.data = [DialogTurn.from_dict(item) if isinstance(item, dict) else item for item in self.data]
        except FileNotFoundError:
            self.data = []  # No data yet, create an empty list
        except json.JSONDecodeError:
            print("Error loading data: The JSON file is malformed or empty.")
            self.data = []  # Handle malformed JSON and initialize an empty list

    def save(self, item):
        """Save a turn or conversation to the local database."""
        if isinstance(item, DialogTurn):
            item = item.to_dict()  # Convert DialogTurn object to dictionary
        elif isinstance(item, list):  # Handle the list of DialogTurn objects (entire conversation)
            item = [turn.to_dict() for turn in item]
        elif isinstance(item, dict):  # Conversation already in dictionary form
            pass
        self.data.append(item)
        self._write_data()

    def _write_data(self):
        """Write the data back to the file."""
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_all_data(self):
        """Retrieve all stored data."""
        return self.data


# DialogTurn Class

class DialogTurn:
    def __init__(self, user_query, assistant_response, user_query_timestamp, assistant_response_timestamp):
        self.user_query = user_query
        self.assistant_response = assistant_response
        self.user_query_timestamp = user_query_timestamp
        self.assistant_response_timestamp = assistant_response_timestamp

    def to_dict(self):
        return {
            "user_query": self.user_query.to_dict(),
            "assistant_response": self.assistant_response.to_dict(),
            "user_query_timestamp": self.user_query_timestamp,
            "assistant_response_timestamp": self.assistant_response_timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_query=UserQuery.from_dict(data["user_query"]),
            assistant_response=AssistantResponse.from_dict(data["assistant_response"]),
            user_query_timestamp=data["user_query_timestamp"],
            assistant_response_timestamp=data["assistant_response_timestamp"]
        )


# UserQuery and AssistantResponse Classes

class UserQuery:
    def __init__(self, query_str):
        self.query_str = query_str

    def to_dict(self):
        return {"query_str": self.query_str}

    @classmethod
    def from_dict(cls, data):
        return cls(data["query_str"])


class AssistantResponse:
    def __init__(self, response_str):
        self.response_str = response_str

    def to_dict(self):
        return {"response_str": self.response_str}

    @classmethod
    def from_dict(cls, data):
        return cls(data["response_str"])


# Initialize Memory

memory = Memory()


# Main program entry point

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Process repository name and base URL.")
    
    # Add arguments for repo_name and base_url
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    parser.add_argument("active_path", type=str, help="It will download in the current path")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Call the main function with the provided arguments
    result = main(args.repo_name, args.base_url, args.active_path)
    
    # Print the result of the main function
    print(result)
    
    # Optionally print the conversation history
    print_conversation_history()


#   python3 history_adalflow.py MortgageApplication https://github.com/gmsadmin-git /Users/thrisham/Desktop/cobol_code/mainframe_final

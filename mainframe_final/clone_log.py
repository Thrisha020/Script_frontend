import os
import subprocess
import shutil
import argparse
import time
from datetime import datetime

# Log file path (same as the one used previously)
LOG_FILE = "internet_connection_log.txt"

# Function to log messages to a file and print to the terminal
def log_to_file(message, LOG_FILE):
    """Logs a message to the log file with a timestamp and prints it to the terminal."""
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - {message}\n"
        log_file.write(log_message)
        log_file.write("-" * 40 + "\n")  # Separator for readability
        print(log_message)  # Print the message to the terminal


def clone_repo(repo_url, clone_path, LOG_FILE):
    try:
        subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
        message = f"Repository cloned successfully to {clone_path}."
        log_to_file(message, LOG_FILE)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error cloning repository: {e}"
        log_to_file(message, LOG_FILE)
        return message

def is_git_repo(folder_path):
    return os.path.isdir(os.path.join(folder_path, ".git"))

def pull_latest_changes(repo_path, LOG_FILE):
    try:
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
        message = f"Latest changes pulled successfully."
        log_to_file(message, LOG_FILE)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error pulling latest changes: {e}"
        log_to_file(message, LOG_FILE)
        return message

def delete_folder(folder_path, LOG_FILE):
    permission = input(f"The folder '{folder_path}' is not a git repository. Do you want to delete it? (yes/no): ").lower()
    if permission == 'yes':
        shutil.rmtree(folder_path)
        log_to_file(f"Folder '{folder_path}' deleted.", LOG_FILE)
        return True
    else:
        log_to_file(f"Operation canceled for folder '{folder_path}'.", LOG_FILE)
        return False

def main(repo_name, base_url, active_path):
    LOG_FILE = f"{active_path}/internet_connection_log.txt"
    #workspace_path = os.getcwd()
    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(active_path, repo_name)

    # Clone if the folder does not exist
    if not os.path.isdir(clone_path):
        log_to_file(f"Cloning repository from {repo_url} to {clone_path}...", LOG_FILE)
        return clone_repo(repo_url, clone_path, LOG_FILE)
    
    # If it's a git repository, pull latest changes
    if is_git_repo(clone_path):
        log_to_file(f"Repository already cloned at {clone_path}. Pulling latest changes...", LOG_FILE)
        return pull_latest_changes(clone_path, LOG_FILE)
    else:
        # Ask for permission to delete the folder and re-clone
        log_to_file(f"Folder '{clone_path}' exists but is not a git repository.", LOG_FILE)
        if delete_folder(clone_path, LOG_FILE):
            log_to_file(f"Re-cloning repository from {repo_url} to {clone_path}...", LOG_FILE)
            return clone_repo(repo_url, clone_path, LOG_FILE)
        else:
            return "Operation canceled."

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

 

#  python3 clone_log.py MortgageApplication https://github.com/gmsadmin-git /Users/thrisham/Desktop/cobol_code/mainframe_final

# 
import os
import subprocess
import shutil
import argparse
from datetime import datetime
import yaml

LOG_FILE = "internet_connection_log.txt"

# Function to log messages to a file and print to the terminal
def log_to_file(message, log_file):
    """Logs a message to the log file with a timestamp and prints it to the terminal."""
    with open(log_file, "a") as log_file_obj:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - {message}\n"
        log_file_obj.write(log_message)
        log_file_obj.write("-" * 40 + "\n")  # Separator for readability
        print(log_message)  # Print the message to the terminal

# Function to load extensions from a YAML file
def load_extensions_from_yaml(file_path):
    """Loads the list of required extensions from the YAML file."""
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return data.get('required_extensions', [])
    except FileNotFoundError:
        message = f"YAML file not found at {file_path}"
        log_to_file(message, LOG_FILE)
        return []
    except yaml.YAMLError as e:
        message = f"Error reading YAML file: {e}"
        log_to_file(message, LOG_FILE)
        return []

# Function to get installed VSCode extensions
def get_installed_extensions():
    """Returns a list of installed VSCode extensions."""
    try:
        result = subprocess.run(['code', '--list-extensions'], stdout=subprocess.PIPE, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        message = f"Error listing extensions: {e}"
        log_to_file(message, LOG_FILE)
        return []

# Function to install a VSCode extension
def install_extension(extension, log_file):
    """Installs the given VSCode extension."""
    try:
        message = f"Installing extension: {extension}"
        log_to_file(message, log_file)
        subprocess.run(['code', '--install-extension', extension, '--force'], check=True)
        message = f"Extension {extension} installed successfully."
        log_to_file(message, log_file)
    except subprocess.CalledProcessError as e:
        message = f"Error installing extension {extension}: {e}"
        log_to_file(message, log_file)

# Function to clone a repository
def clone_repo(repo_url, clone_path, log_file):
    try:
        subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
        message = f"Repository cloned successfully to {clone_path}."
        log_to_file(message, log_file)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error cloning repository: {e}"
        log_to_file(message, log_file)
        return message

# Function to check if a folder is a git repository
def is_git_repo(folder_path):
    return os.path.isdir(os.path.join(folder_path, ".git"))

# Function to pull the latest changes from a git repository
def pull_latest_changes(repo_path, log_file):
    try:
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
        message = f"Latest changes pulled successfully."
        log_to_file(message, log_file)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error pulling latest changes: {e}"
        log_to_file(message, log_file)
        return message

# Function to delete a folder
def delete_folder(folder_path, log_file):
    permission = input(f"The folder '{folder_path}' is not a git repository. Do you want to delete it? (yes/no): ").lower()
    if permission == 'yes':
        shutil.rmtree(folder_path)
        message = f"Folder '{folder_path}' deleted."
        log_to_file(message, log_file)
        return True
    else:
        message = f"Operation canceled for folder '{folder_path}'."
        log_to_file(message, log_file)
        return False

# Function to find a file in a repository
def find_file_in_repo(repo_path, file_name, log_file):
    """Search for the file in the repo and return its path if found."""
    log_to_file(f"Searching for file '{file_name}' in repository '{repo_path}'", log_file)
    for root, dirs, files in os.walk(repo_path):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            log_to_file(f"File found: {file_path}", log_file)
            return file_path
    log_to_file(f"File '{file_name}' not found in repository '{repo_path}'", log_file)
    return None

# Function to open a file in VSCode
def open_in_vscode(file_path, log_file):
    """Open the file in VSCode."""
    try:
        log_to_file(f"Attempting to open file in VSCode: {file_path}", log_file)
        subprocess.run(["code", file_path], check=True)
        message = f"File opened successfully in VSCode: {file_path}"
        log_to_file(message, log_file)
        return "File opened"
    except FileNotFoundError:
        message = "VSCode not installed or 'code' command not available."
        log_to_file(message, log_file)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error opening file in VSCode: {e}"
        log_to_file(message, log_file)
        return message

# Main function
def main(required_extensions, repo_name, base_url, file_name, active_folder_path):
    log_file = f"{active_folder_path}/internet_connection_log.txt"

    installed_extensions = get_installed_extensions()
    for extension in required_extensions:
        if extension not in installed_extensions:
            install_extension(extension, log_file)
        else:
            log_to_file(f"Extension {extension} is already installed.", log_file)

    repo_name = repo_name.split("/")[-1]
    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(active_folder_path, repo_name)

    if not os.path.isdir(clone_path):
        log_to_file(f"Cloning repository from {repo_url} to {clone_path}...", LOG_FILE)
        clone_repo(repo_url, clone_path, LOG_FILE)
        return (f"Cloning repository from {repo_url} to {clone_path}..." ,LOG_FILE)

    if is_git_repo(clone_path):
        log_to_file(f"Repository already cloned at {clone_path}. Pulling latest changes...", LOG_FILE)
        pull_latest_changes(clone_path, LOG_FILE)
        return (f"Repository already cloned at {clone_path}. Pulling latest changes...",LOG_FILE)
    else:
        log_to_file(f"Folder '{clone_path}' exists but is not a git repository.", LOG_FILE)
        delete_folder(clone_path, log_file)
        log_to_file(f"Re-cloning repository from {repo_url} to {clone_path}...", LOG_FILE)
        clone_repo(repo_url, clone_path, log_file)

    file_path = find_file_in_repo(clone_path, file_name, log_file)

    if file_path:
        result = open_in_vscode(file_path, log_file)
        if result == "File opened":
            return f"Successfully opened: {file_path}"
        else:
            return result
    else:
        message = f"File '{file_name}' not found in repository '{repo_name}'."
        log_to_file(message, log_file)
        return message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process repository name, base URL, file name, and active folder path.")
    parser.add_argument("required_extensions", type=str, nargs="+", help="List of extensions to be installed")
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    parser.add_argument("file_name", type=str, help="The name of the file to open")
    parser.add_argument("active_folder_path", type=str, help="The path of the active workspace folder")
    args = parser.parse_args()

    result = main(args.required_extensions, args.repo_name, args.base_url, args.file_name, args.active_folder_path)
    print(result)

# python3 log_testing.py IBM.zopeneditor ms-vscode-remote.remote-ssh Thrisha020/MortgageApplication https://github.com/Thrisha020/ hello.cbl /Users/thrisham/Desktop/cobol_code/mainframe_final
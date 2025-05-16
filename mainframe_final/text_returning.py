import os
import subprocess
import shutil
import argparse
from datetime import datetime
import yaml

# Log file path (same as the one used previously)
LOG_FILE = "internet_connection_log.txt"

def log_to_file(message, log_file):
    """Logs a message to the log file with a timestamp."""
    # Use a fallback log file path if the primary path is read-only
    if not os.access(os.path.dirname(log_file), os.W_OK):
        log_file = os.path.expanduser("~/fallback_internet_connection_log.txt")
        print(f"Falling back to log file at: {log_file}")
    
    with open(log_file, "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - {message}\n"
        file.write(log_message)
        file.write("-" * 40 + "\n")

def load_extensions_from_yaml(file_path):
    """Loads the list of required extensions from the YAML file."""
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return data.get('required_extensions', [])
    except FileNotFoundError:
        return log_to_file_and_return(f"YAML file not found at {file_path}", LOG_FILE)
    except yaml.YAMLError as e:
        return log_to_file_and_return(f"Error reading YAML file: {e}", LOG_FILE)

def get_installed_extensions():
    """Returns a list of installed VSCode extensions."""
    try:
        result = subprocess.run(['code', '--list-extensions'], stdout=subprocess.PIPE, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        return log_to_file_and_return(f"Error listing extensions: {e}", LOG_FILE)

def install_extension(extension):
    """Installs the given VSCode extension."""
    try:
        message = f"Installing extension: {extension}"
        log_to_file_and_return(message, LOG_FILE)
        subprocess.run(['code', '--install-extension', extension, '--force'], check=True)
        return log_to_file_and_return(f"Extension {extension} installed successfully.", LOG_FILE)
    except subprocess.CalledProcessError as e:
        return log_to_file_and_return(f"Error installing extension {extension}: {e}", LOG_FILE)

def clone_repo(repo_url, clone_path, LOG_FILE):
    try:
        subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
        return log_to_file_and_return(f"Repository cloned successfully to {clone_path}.", LOG_FILE)
    except subprocess.CalledProcessError as e:
        return log_to_file_and_return(f"Error cloning repository: {e}", LOG_FILE)

def is_git_repo(folder_path):
    return os.path.isdir(os.path.join(folder_path, ".git"))

def pull_latest_changes(repo_path, LOG_FILE):
    try:
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
        return log_to_file_and_return(f"Latest changes pulled successfully.", LOG_FILE)
    except subprocess.CalledProcessError as e:
        return log_to_file_and_return(f"Error pulling latest changes: {e}", LOG_FILE)

def delete_folder(folder_path, LOG_FILE):
    permission = input(f"The folder '{folder_path}' is not a git repository. Do you want to delete it? (yes/no): ").lower()
    if permission == 'yes':
        shutil.rmtree(folder_path)
        return log_to_file_and_return(f"Folder '{folder_path}' deleted.", LOG_FILE)
    else:
        return log_to_file_and_return(f"Operation canceled for folder '{folder_path}'.", LOG_FILE)

def find_file_in_repo(repo_path, file_name, LOG_FILE):
    """Search for the file in the repo and return its path if found."""
    log_to_file_and_return(f"Searching for file '{file_name}' in repository '{repo_path}'", LOG_FILE)
    for root, dirs, files in os.walk(repo_path):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            return log_to_file_and_return(f"File found: {file_path}", LOG_FILE)
    return log_to_file_and_return(f"File '{file_name}' not found in repository '{repo_path}'", LOG_FILE)

def open_in_vscode(file_path, LOG_FILE):
    """Open the file in VSCode."""
    try:
        log_to_file_and_return(f"Attempting to open file in VSCode: {file_path}", LOG_FILE)
        subprocess.run(["code", file_path], check=True)
        return log_to_file_and_return(f"File opened successfully in VSCode: {file_path}", LOG_FILE)
    except FileNotFoundError:
        return log_to_file_and_return("VSCode not installed or 'code' command not available.", LOG_FILE)
    except subprocess.CalledProcessError as e:
        return log_to_file_and_return(f"Error opening file in VSCode: {e}", LOG_FILE)

def main(required_extensions, repo_name, base_url, file_name, active_folder_path):
    installed_extensions = get_installed_extensions()
    for extension in required_extensions:
        if extension not in installed_extensions:
            install_extension(extension)

    LOG_FILE = f"{active_folder_path}/internet_connection_log.txt"
    repo_name = repo_name.split("/")[-1]
    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(active_folder_path, repo_name)

    if not os.path.isdir(clone_path):
        log_to_file_and_return(f"Cloning repository from {repo_url} to {clone_path}...", LOG_FILE)
        clone_repo(repo_url, clone_path, LOG_FILE)

    if is_git_repo(clone_path):
        log_to_file_and_return(f"Repository already cloned at {clone_path}. Pulling latest changes...", LOG_FILE)
        pull_latest_changes(clone_path, LOG_FILE)
    else:
        log_to_file_and_return(f"Folder '{clone_path}' exists but is not a git repository.", LOG_FILE)
        delete_folder(clone_path, LOG_FILE)

    file_path = find_file_in_repo(clone_path, file_name, LOG_FILE)
    if file_path:
        return open_in_vscode(file_path, LOG_FILE)
    else:
        return log_to_file_and_return(f"File '{file_name}' not found in repository '{repo_name}'.", LOG_FILE)

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


# python3 text_returning.py IBM.zopeneditor ms-vscode-remote.remote-ssh Thrisha020/MortgageApplication https://github.com/Thrisha020/ hello.cbl /Users/thrisham/Desktop/cobol_code/mainframe_final
import os
import subprocess
import shutil
import argparse
from datetime import datetime
import yaml,json
# Log file path (same as the one used previously)
LOG_FILE = "internet_connection_log.txt"

def load_extensions_from_yaml(file_path):
    """Loads the list of required extensions from the YAML file."""
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return data.get('required_extensions', [])
    except FileNotFoundError:
        print(f"YAML file not found at {file_path}")
        return []
    except yaml.YAMLError as e:
        print(f"Error reading YAML file: {e}")
        return []
    


# Function to log messages to a file and print to the terminal
def log_to_file(message, LOG_FILE):
    """Logs a message to the log file with a timestamp and prints it to the terminal."""
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - {message}\n"
        log_file.write(log_message)
        log_file.write("-" * 40 + "\n")  # Separator for readability
        print(log_message)  # Print the message to the terminal

def get_installed_extensions():
    """Returns a list of installed VSCode extensions."""
    try:
        result = subprocess.run(['code', '--list-extensions'], stdout=subprocess.PIPE, text=True, check=True)
        installed_extensions = result.stdout.splitlines()
        return installed_extensions
    except subprocess.CalledProcessError as e:
        message = f"Error listing extensions: {e}."
        log_to_file(message, LOG_FILE)
        return message


def install_extension(extension):
    """Installs the given VSCode extension."""
    try:
        print(f"Installing extension: {extension}")
        subprocess.run(['code', '--install-extension', extension, '--force'], check=True)
        message = f"Extension {extension} installed successfully."
        log_to_file(message, LOG_FILE)
        return message
    except subprocess.CalledProcessError as e:
        print(f"Error installing extension {extension}: {e}")


# def clone_repo(repo_url, clone_path, LOG_FILE):
def clone_repo(repo_url, clone_path,LOG_FILE,branch='Feature/Demo'):
    try:
        print("Feature_branch")
        subprocess.run(['git', 'clone', '-b', branch, repo_url, clone_path], check=True)
        message = f"Repository cloned successfully to {clone_path}."
        log_to_file(message, LOG_FILE)
        return message
    except subprocess.CalledProcessError as e:
        message = f"Error cloning repository: {e}"
        log_to_file(message, LOG_FILE)
        return message
# def clone_repo(repo_url, clone_path, branch='feature_branch'):
#     try:
#         subprocess.run(['git', 'clone', '-b', branch, repo_url, clone_path], check=True)
#         return f"Repository cloned successfully from '{branch}' branch to {clone_path}."
#     except subprocess.CalledProcessError as e:
#         return f"Error cloning repository from '{branch}' branch: {e}"


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


def find_file_in_repo(repo_path, file_name, LOG_FILE):
    """Search for the file in the repo and return its path if found."""
    log_to_file(f"Searching for file '{file_name}' in repository '{repo_path}'", LOG_FILE)
    for root, dirs, files in os.walk(repo_path):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            log_to_file(f"File found: {file_path}", LOG_FILE)
            return file_path
    log_to_file(f"File '{file_name}' not found in repository '{repo_path}'", LOG_FILE)
    return None


def open_in_vscode(file_path, LOG_FILE):
    """Open the file in VSCode."""
    try:
        log_to_file(f"Attempting to open file in VSCode: {file_path}", LOG_FILE)
        subprocess.run(["code", file_path], check=True)
        log_to_file(f"File opened successfully in VSCode: {file_path}", LOG_FILE)
        return "File opened"
    except FileNotFoundError:
        log_to_file("VSCode not installed or 'code' command not available.", LOG_FILE)
        return "VSCode not installed or 'code' command not available. Please install and configure it."
    except subprocess.CalledProcessError as e:
        log_to_file(f"Error opening file in VSCode: {e}", LOG_FILE)
        return f"Error opening file in VSCode: {e}"


def main(required_extensions, repo_name, base_url, file_name, active_folder_path):

    LOG_FILE = f"{active_folder_path}/internet_connection_log.txt"

    installed_extensions = get_installed_extensions()
    for extension in required_extensions:
        if extension not in installed_extensions:
            #print(f"Extension {extension} is not installed. Installing...")
            #print(json.dumps({"status": "success", "message": f"Extension {extension} is not installed. Installing..."}))
            log_to_file(f"Extension {extension} is not installed. Installing...", LOG_FILE)
            install_extension(extension)
            
        else:
            #print(f"Extension {extension} is already installed.")
            log_to_file(f"Extension {extension} is already installed.", LOG_FILE)
            #print(json.dumps({ "message": f"Extension {extension} is already installed."}))
            

    #print("\nVerifying installed extensions...")
    #print(json.dumps({"status": "error", "message": "\nVerifying installed extensions..."}))
    installed_extensions = get_installed_extensions()
    for extension in required_extensions:
        if extension in installed_extensions:
            log_to_file(f"Extension {extension} is installed and verified.", LOG_FILE)
            #print(f"Extension {extension} is installed and verified.")
          
            #print(json.dumps({"status": "success", "message": f"Extension {extension} is installed and verified."}))
        else:
            log_to_file(f"Extension {extension} is still not installed.", LOG_FILE)
        
    repo_url = f"{base_url}/{repo_name}.git"

    base_name = repo_name.split("/")[0]
    repo_name = repo_name.split("/")[-1]

    base_url = f'{base_url}/{base_name}/'

    ##### working one
    # repo_name = repo_name.split("/")[-1]
    # repo_url = f"{base_url}/{repo_name}.git"
    
    clone_path = os.path.join(active_folder_path, repo_name)

    # Clone if the folder does not exist
    if not os.path.isdir(clone_path):
        log_to_file(f"Cloning repository from {repo_url} to {clone_path}...", LOG_FILE)
        clone_repo(repo_url, clone_path, LOG_FILE)

    # If it's a git repository, pull latest changes
    if is_git_repo(clone_path):
        log_to_file(f"Repository already cloned at {clone_path}. Pulling latest changes...", LOG_FILE)
        pull_latest_changes(clone_path, LOG_FILE)
    else:
        # Ask for permission to delete the folder and re-clone
        log_to_file(f"Folder '{clone_path}' exists but is not a git repository.", LOG_FILE)
        #if delete_folder(clone_path, LOG_FILE):
            #log_to_file(f"Re-cloning repository from {repo_url} to {clone_path}...", LOG_FILE)
            #clone_repo(repo_url, clone_path, LOG_FILE)
        #else:
            #log_to_file("Operation canceled.", LOG_FILE)
            #return "Operation canceled."

    log_to_file(f"Starting process for repository: {repo_name} at {base_url}", LOG_FILE)
    log_to_file(f"Local repository path: {clone_path}", LOG_FILE)

    # Find the file in the repository (including subdirectories)
    file_path = find_file_in_repo(clone_path, file_name, LOG_FILE)

    if file_path:
        log_to_file(f"File located: {file_path}. Attempting to open in VSCode.", LOG_FILE)
        result = open_in_vscode(file_path, LOG_FILE)
        if result == "File opened":
            log_to_file(f"Successfully opened: {file_path}", LOG_FILE)
            #return f"Successfully opened: {file_path}"
            print(json.dumps({"message": f"Successfully opened: {file_path}"}))
            return
        else:
            log_to_file(result, LOG_FILE)
            #return result
            print(json.dumps({"message": result}))
            return
        
    else:
        message = f"File '{file_name}' not found in repository '{repo_name}'."
        log_to_file(message, LOG_FILE)
        #return message
        print(json.dumps({"message": result}))
        return


if __name__ == "__main__":
    # Create an argument parser

    parser = argparse.ArgumentParser(description="Process repository name, base URL, file name, and active folder path.")
    parser.add_argument("required_extensions", type=str,nargs="+", help="List of extension to be installed")
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    parser.add_argument("file_name", type=str, help="The name of the file to open")
    parser.add_argument("active_folder_path", type=str, help="The path of the active workspace folder")
    args = parser.parse_args()

    # Execute the main function
    print(main(args.required_extensions ,args.repo_name, args.base_url, args.file_name, args.active_folder_path))
    # print(json.dumps({"status": "error", "message": "Missing required arguments."}))

    # print(result)



# python3 open_clone.py Thrisha020/MortgageApplication https://github.com hello.cbl /Users/thrisham/Desktop/cobol_code/mainframe_final



# python3 open_clone.py IBM.zopeneditor ms-vscode-remote.remote-ssh Thrisha020/MortgageApplication https://github.com hello.cbl /Users/thrisham/Desktop/cobol_code/mainframe_final


#   python3 open_clone.py IBM.zopeneditor ms-vscode-remote.remote-ssh gmsadmin-git/MortgageApplication https://github.com hello.cbl /Users/thrisham/Desktop/cobol_code/mainframe_final
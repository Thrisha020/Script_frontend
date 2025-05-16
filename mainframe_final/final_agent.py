
"""
Author:Thrisha M

Date:31th dec 2024

USE IT FOR INTERNATIONALIZATION

"""


import os
import subprocess
import requests
import time
import yaml
import shutil

SERVER_URL = "http://10.190.226.6:8000/repository"

import platform
import os
import webbrowser
import shutil
import paramiko
from getpass import getpass
import subprocess


# Function to read the YAML configuration file
def load_config(yaml_file='vscode_extension.yaml'):  # Default file name
    script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the directory of the running script
    yaml_path = os.path.join(script_dir, yaml_file)  # Construct the full path to the YAML file
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    else:
        raise FileNotFoundError(f"Configuration file '{yaml_file}' not found at path: {yaml_path}")


# Function to check if VSCode is installed on Windows
def open_vscode_windows():
    config = load_config()  # Read YAML config
    try:
        subprocess.run(["powershell", "-Command", "code"])
        return "VSCode has been launched on Windows."
    except FileNotFoundError:
        print("VSCode not found. Opening the download page and displaying installation instructions.")
        webbrowser.open(config['windows_vscode_download_link'])  # Use the download link from YAML
        display_instructions(config['windows_instruction_path'])  # Use the instruction path from YAML
        return "VSCode not found. Download link opened."
    except Exception as e:
        return f"Failed to open VSCode on Windows: {str(e)}"


# Function to check if VSCode is installed on Mac
def open_vscode_mac():
    config = load_config()  # Read YAML config
    try:
        subprocess.run(["open", "-a", "Visual Studio Code"])
        return "VSCode has been launched on Mac."
    except FileNotFoundError:
        print("VSCode not found. Opening the download page and displaying installation instructions.")
        webbrowser.open(config['mac_vscode_download_link'])  # Use the download link from YAML
        display_instructions(config['mac_instruction_path'])  # Use the instruction path from YAML
        return "VSCode not found. Download link opened."
    except Exception as e:
        return f"Failed to open VSCode on Mac: {str(e)}"
    
# Function to check if VSCode is installed on Linux
def open_vscode_linux():
    config = load_config()  # Read YAML config
    try:
        subprocess.run(["code"])  # Linux command to open VSCode
        return "VSCode has been launched on Linux."
    except FileNotFoundError:
        print("VSCode not found. Opening the download page and displaying installation instructions.")
        webbrowser.open(config['linux_vscode_download_link'])  # Use the download link from YAML
        display_instructions(config['linux_instruction_path'])  # Use the instruction path from YAML
        return "VSCode not found. Download link opened."
    except Exception as e:
        return f"Failed to open VSCode on Linux: {str(e)}"


# Function to display instructions (e.g., PDF)
def display_instructions(file_path):
    if os.path.exists(file_path):
        print(f"Opening the instruction file: {file_path}")
        webbrowser.open(f"file://{file_path}")
    else:
        print(f"Instruction file not found at {file_path}")


# Function to check internet connection and speed
def check_internet_connection():
    """Checks if there is an active internet connection."""
    test_url = 'https://www.google.com'
    timeout = 5
    try:
        start_time = time.time()
        response = requests.get(test_url, timeout=timeout)
        end_time = time.time()

        if response.status_code == 200:
            elapsed_time = end_time - start_time
            content_size = len(response.content)

            speed_bps = content_size / elapsed_time
            speed_kbps = speed_bps / 1024
            speed_mbps = speed_kbps / 1024

            print("Internet connection is available.")
            print(f"Speed: {speed_kbps:.2f} KB/s ({speed_mbps:.2f} MB/s)")
            return True
        else:
            print("No internet connection.")
            return False

    except (requests.ConnectionError, requests.Timeout):
        print("No internet connection.")
        return False


# Function to load extensions from YAML file
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


# Function to retrieve the list of installed VSCode extensions
def get_installed_extensions():
    """Returns a list of installed VSCode extensions."""
    try:
        result = subprocess.run(['code', '--list-extensions'], stdout=subprocess.PIPE, text=True, check=True)
        installed_extensions = result.stdout.splitlines()
        return installed_extensions
    except subprocess.CalledProcessError as e:
        print(f"Error listing extensions: {e}")
        return []


# Function to install a specific VSCode extension
def install_extension(extension):
    """Installs the given VSCode extension."""
    try:
        print(f"Installing extension: {extension}")
        subprocess.run(['code', '--install-extension', extension, '--force'], check=True)
        print(f"Extension {extension} installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing extension {extension}: {e}")

# Check if the file exists locally
def file_exists(file_path):
    return os.path.isfile(file_path)

# Check if a folder is a Git repository
def is_git_repo(folder_path):
    return os.path.isdir(os.path.join(folder_path, ".git"))

#Search for repositories matching the prefix using GitHub API
def search_repositories(git_url, prefix):
    """Search for repositories matching the prefix using GitHub API."""
    search_url = f"{git_url}/search/repositories"
    params = {"q": f"{prefix} in:name"}
    headers = {"Accept": "application/vnd.github+json"}
    
    try:
        response = requests.get(search_url, params=params, headers=headers)
        response.raise_for_status()
        repositories = response.json().get("items", [])
        return [repo["name"] for repo in repositories]
    except requests.RequestException as e:
        print(f"Error searching repositories: {e}")
        return []


# Delete the local folder with user permission
def delete_folder(folder_path):
    permission = input(f"The folder '{folder_path}' is not a git repository. Do you want to delete it? (yes/no): ").lower()
    if permission == 'yes':
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' deleted.")
        return True
    else:
        print("Operation canceled. Exiting.")
        return False


# Open the file in VSCode
def open_in_vscode(file_path):
    try:
        subprocess.run(["code", file_path], check=True)
    except FileNotFoundError:
        print("VSCode is not installed. Please install VSCode from https://code.visualstudio.com/")
    except subprocess.CalledProcessError as e:
        print(f"Error opening file in VSCode: {e}")

# Clone the repository
def clone_repo(repo_url, clone_path):
    try:
        subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
        print(f"Repository cloned successfully to {clone_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")


# Pull the latest changes from the repository
def pull_latest_changes(repo_path):
    try:
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
        print("Latest changes pulled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error pulling latest changes: {e}")


# List all branches in the repo
def list_branches(repo_path):
    """List all available branches in the repository."""
    try:
        result = subprocess.run(['git', '-C', repo_path, 'branch', '-a'], check=True, text=True, capture_output=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error listing branches: {e}")
        return []
    

# Checkout the selected branch

def checkout_branch(repo_path, branch_name):
    """Try to checkout a branch, handle errors, and fallback if needed."""
    try:
        subprocess.run(['git', '-C', repo_path, 'checkout', branch_name], check=True)
        print(f"Checked out branch '{branch_name}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking out branch '{branch_name}': {e}")
        fallback_branch = "main"  # Default fallback branch
        print(f"Attempting to checkout fallback branch '{fallback_branch}'.")
        try:
            subprocess.run(['git', '-C', repo_path, 'checkout', fallback_branch], check=True)
            print(f"Checked out fallback branch '{fallback_branch}' successfully.")
        except subprocess.CalledProcessError as fallback_error:
            print(f"Failed to checkout fallback branch '{fallback_branch}': {fallback_error}")

# Function to find a file recursively in a repository
def find_file_in_repo(repo_path, file_name):
    for root, dirs, files in os.walk(repo_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None


# Push the new branch to GitHub
def push_branch(repo_path, branch_name):
    """Push a new branch to the remote repository."""
    try:
        subprocess.run(['git', '-C', repo_path, 'push', '-u', 'origin', branch_name], check=True)
        print(f"Branch '{branch_name}' pushed to remote repository.")
    except subprocess.CalledProcessError as e:
        print(f"Error pushing branch '{branch_name}': {e}")



# Establish SSH connection and get mainframe's current working directory
def create_ssh_connection(hostname, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname, port=port, username=username, password=password)
        print("Connection successful!")
        stdin, stdout, stderr = ssh.exec_command("pwd")
        mainframe_pwd = stdout.read().decode().strip()
        print(f"Mainframe working directory: {mainframe_pwd}")
        return ssh, mainframe_pwd
    except Exception as e:
        print(f"SSH connection failed: {e}")
    return None, None

# Check and create required subdirectories
def check_and_create_directories(ssh, mainframe_pwd, application, workspace_name="sandbox1"):
    try:
        # Dynamically construct paths
        workspace_path = f"{mainframe_pwd}/{workspace_name}"
        application_path = f"{workspace_path}/{application}"

        # Ensure workspace directory exists
        print(f"Ensuring workspace directory: {workspace_path}")
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {workspace_path}")
        if stderr.read().strip():
            raise Exception(f"Failed to create workspace directory: {workspace_path}")

        # Ensure application directory exists
        print(f"Ensuring application directory: {application_path}")
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {application_path}")
        if stderr.read().strip():
            raise Exception(f"Failed to create application directory: {application_path}")

        return workspace_path, application_path
    except Exception as e:
        print(f"Error creating directories: {e}")
        return None, None


# Function to find a file recursively in a repository
def find_file_in_repo(repo_path, file_name):
    for root, dirs, files in os.walk(repo_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

# Check if Git Repository is Present; if not, Clone
# Adjust `check_or_clone_repository` to enforce GitHub cloning
def check_or_clone_repository(ssh, repo_url, application_path):
    """
    Check if a Git repository exists on the mainframe.
    If not, clone the repository. If it exists, pull the latest changes.
    """
    try:
        # Check if the repository already exists
        check_git_repo_cmd = f"if [ -d {application_path}/.git ]; then echo 'found'; else echo 'not_found'; fi"
        stdin, stdout, stderr = ssh.exec_command(check_git_repo_cmd)
        repo_status = stdout.read().decode().strip()

        if repo_status == 'not_found':
            print(f"No Git repository found at {application_path}. Cloning the repository...")
            clone_command = f"""
                export GIT_SHELL=/usr/lpp/Rocket/rsusr/ported/bin/bash && \
                export GIT_EXEC_PATH=/usr/lpp/Rocket/rsusr/ported/libexec/git-core && \
                export GIT_TEMPLATE_DIR=/usr/lpp/Rocket/rsusr/ported/share/git-core/templates && \
                export GIT_MAN_PATH=/usr/lpp/Rocket/rsusr/ported/share/man && \
                export PATH=$PATH:/usr/lpp/Rocket/rsusr/ported/bin && \
                git clone {repo_url} {application_path}
            """
            stdin, stdout, stderr = ssh.exec_command(clone_command)
            clone_output = stdout.read().decode().strip()
            clone_error = stderr.read().decode().strip()
            if clone_error:
                raise Exception(f"Clone error: {clone_error}")
            print("Repository cloned successfully.")
        else:
            print(f"Repository already exists at {application_path}. Pulling latest changes...")
            pull_command = f"""
                export GIT_SHELL=/usr/lpp/Rocket/rsusr/ported/bin/bash && \
                export GIT_EXEC_PATH=/usr/lpp/Rocket/rsusr/ported/libexec/git-core && \
                export GIT_TEMPLATE_DIR=/usr/lpp/Rocket/rsusr/ported/share/git-core/templates && \
                export GIT_MAN_PATH=/usr/lpp/Rocket/rsusr/ported/share/man && \
                export PATH=$PATH:/usr/lpp/Rocket/rsusr/ported/bin && \
                cd {application_path} && git pull
            """
            stdin, stdout, stderr = ssh.exec_command(pull_command)
            pull_output = stdout.read().decode().strip()
            pull_error = stderr.read().decode().strip()
            if pull_error:
                raise Exception(f"Pull error: {pull_error}")
            print("Latest changes pulled successfully.")
    except Exception as e:
        print(f"Error during repository setup: {e}")



def change_to_git_repo(ssh, application_path):
    try:
        ssh.exec_command(f"cd {application_path}")
        print(f"Changed to application repo at: {application_path}")
    except Exception as e:
        print(f"Failed to change to git repo directory: {e}")

# Perform Git Pull and Branch Checkout
def git_pull_and_checkout(ssh, application_path, branch_name):
    try:
        ssh.exec_command(f"cd {application_path} && git pull && git checkout {branch_name}")
        print(f"Checked out branch '{branch_name}'")
    except Exception as e:
        print(f"Git pull or checkout failed: {e}")

# Search for the Absolute Path of the Source File Dynamically
def find_source_file(ssh, application_path, filename):
    try:
        print(f"Searching for '{filename}' in '{application_path}'...")

        # Case-sensitive search using `-name`
        find_command = f"find {application_path} -type f -name \"{filename}\""
        print(f"Executing: {find_command}")

        stdin, stdout, stderr = ssh.exec_command(find_command)
        file_path = stdout.read().decode().strip()  # Capture the found file path
        error_output = stderr.read().decode().strip()  # Capture any error output

        print(f"Find Command Output: {file_path}")
        if error_output:
            print(f"Find Command Errors: {error_output}")

        # If file is not found and case sensitivity might be an issue
        if not file_path:
            print(f"File not found using exact name match. Trying case-insensitive search...")
            list_command = f"ls -R {application_path}"
            stdin, stdout, stderr = ssh.exec_command(list_command)
            all_files = stdout.read().decode().strip().split("\n")
            matching_files = [f for f in all_files if filename.lower() in f.lower()]
            
            if matching_files:
                file_path = f"{application_path}/{matching_files[0]}"
                print(f"Case-insensitive match found: {file_path}")
            else:
                raise FileNotFoundError(f"Source file '{filename}' not found in the application directory.")

        return file_path  # Return the found file path
    except Exception as e:
        print(f"Error finding source file: {e}")
        return None


# Updated run_mainframe_commands to dynamically handle folder_name
# Run mainframe commands and log messages to a file
def run_mainframe_commands(ssh, hlq, application, filename, file_path, config, workspace, outdir):
    try:
        folder_name = os.path.dirname(file_path) if file_path else ""
        
        if not folder_name:
            raise ValueError("Cannot determine the folder name. The source file path is invalid.")
        
        print(f"Ensuring output directory exists: {outdir}")
        ssh.exec_command(f"mkdir -p {outdir}")
        
        groovyzpath = config.get('groovyzpath')
        zappbuildpath = config.get('zappbuildpath')
        
        if not groovyzpath or not zappbuildpath:
            raise ValueError("Missing groovyzpath or zappbuildpath in configuration.")
        
        # Construct the command
        uss_command = (
            f". ~/.profile && "
            f"{groovyzpath} "
            f"{zappbuildpath} -DBB_PERSONAL_DAEMON --workspace {workspace} "
            f"--application {application} --outDir {outdir} "
            f"--hlq {hlq} {folder_name}/{filename} --verbose"
        )

# Executing USS Command: /u/gmszfs/dbb20/usr/lpp/IBM/dbb/bin/groovyz -DBB_PERSONAL_DAEMON /u/gmsratn/zAppbuild20/Development/build.groovy 
# --workspace /u/gmsratn/workspace --application MortgageApplication --outDir /u/gmsratn/outdir 
# --hlq GMSRATN /u/gmsratn/workspace/MortgageApplication/cobol/hello.cbl --verbose
        print(f"Executing USS Command: {uss_command}")
        
        # Execute the command and stream output in real-time
        stdin, stdout, stderr = ssh.exec_command(uss_command)
        
        stdout_output = []
        stderr_output = []

        print("Command output (stdout):")
        for line in iter(stdout.readline, ""):
            print(line.strip())
            stdout_output.append(line.strip())

        print("Command error output (stderr):")
        for line in iter(stderr.readline, ""):
            print(line.strip())
            stderr_output.append(line.strip())

        # Join outputs to return as a single string
        return "\n".join(stdout_output), "\n".join(stderr_output)
    except Exception as e:
        error_message = f"Failed to execute build command: {e}"
        print(error_message)
        return None, error_message


# Upload directory recursively to the mainframe
def upload_directory_to_mainframe(sftp, local_path, remote_path):
    try:
        for root, dirs, files in os.walk(local_path):
            # Skip `.git` directories
            if '.git' in root:
                continue

            # Translate local path to remote path
            relative_path = os.path.relpath(root, local_path)
            remote_dir = os.path.join(remote_path, relative_path).replace("\\", "/")
            
            try:
                sftp.mkdir(remote_dir)
                print(f"Created remote directory: {remote_dir}")
            except IOError:  # Directory already exists
                print(f"Remote directory already exists: {remote_dir}")
            
            for file in files:
                local_file = os.path.join(root, file)
                remote_file = os.path.join(remote_dir, file).replace("\\", "/")
                sftp.put(local_file, remote_file)
                print(f"Uploaded file: {local_file} to {remote_file}")
    except Exception as e:
        print(f"Error uploading directory: {e}")


# Analyze Logs and Display Build Status
def analyze_build_logs(output, error_output):
    if error_output:
        print("Build failed.")
        print(f"Error Logs:\n{error_output}")
    else:
        print("Build succeeded.")
        print(f"Build Output:\n{output}")

def handle_server_command(action, config_path):

            current_dir = os.path.dirname(os.path.abspath(__file__))

            os_name = platform.system()
            print(f"Detected OS: {os_name}")

            if action == "open_vscode":
                print("Opening VS Code...")
                if os_name == "Windows":
                    message = open_vscode_windows()
                elif os_name == "Darwin":  # macOS
                    message = open_vscode_mac()
                else:
                    print(f"Your operating system ({os_name}) is not supported. Currently, only Windows and macOS are supported.")
                    return
                print(message)

            elif action == "check_internet":
                if not check_internet_connection():
                    print("No internet. Please check your connection and try again.")

            elif action == "install_extensions":
                yaml_file = 'vscode_extension.yaml'  # Default YAML file
                required_extensions = load_extensions_from_yaml(yaml_file)
                if not required_extensions:
                    print("No extensions found in the YAML file. Please ensure the file exists and is correctly formatted.")
                    return

                installed_extensions = get_installed_extensions()
                for extension in required_extensions:
                    if extension not in installed_extensions:
                        print(f"Extension {extension} is not installed. Installing...")
                        install_extension(extension)
                    else:
                        print(f"Extension {extension} is already installed.")

                print("\nVerifying installed extensions...")
                installed_extensions = get_installed_extensions()
                for extension in required_extensions:
                    if extension in installed_extensions:
                        print(f"Extension {extension} is installed and verified.")
                    else:
                        print(f"Extension {extension} is still not installed.")
                
            config_path = os.path.join(os.getcwd(), 'pull_clone.yaml')
            config = load_config(config_path)
            if not config:
                return

            base_url = config['repository']['base_url']
            workspace_path = os.getcwd()
            repo_name = input("Enter the repository name: ")
            repo_url = f"{base_url}/{repo_name}.git"
            clone_path = os.path.join(workspace_path, repo_name)

            if action == "clone":
                if not os.path.isdir(clone_path):
                    print(f"Cloning repository from {repo_url} to {clone_path}...")
                    clone_repo(repo_url, clone_path)
                
                # Verify if the folder is a Git repository
                if is_git_repo(clone_path):
                    print(f"Repository already cloned at {clone_path}. Pulling latest changes...")
                    pull_latest_changes(clone_path)
                else:
                    # Ask for permission to delete the folder
                    if delete_folder(clone_path):
                        print(f"Re-cloning repository from {repo_url} to {clone_path}...")
                        clone_repo(repo_url, clone_path)
                    else:
                        return

            elif action == "list_branches":
                if not is_git_repo(clone_path):
                    print(f"Error: {clone_path} is not a valid Git repository.")
                    return
                
                branches = list_branches(clone_path)
                if branches:
                    print("Available branches:")
                    for i, branch in enumerate(branches, start=1):
                        print(f"{i}. {branch}")
                    # Ask if the user wants to create a new branch or use an existing one
                    

            elif action == "checkout_branch":
            # First, check if the repository is valid
                if not is_git_repo(clone_path):
                    print(f"Error: {clone_path} is not a valid Git repository.")
                    return
                
                # List the branches if not already done
                branches = list_branches(clone_path)
                if branches:
                    #print("Available branches:")
                    #for i, branch in enumerate(branches, start=1):
                        #print(f"{i}. {branch}")
                    
                    action = input("Do you want to checkout an existing branch or create a new one? (enter 'existing' or 'new'): ").lower()

                    if action == 'existing':
                        branch_num = int(input(f"Enter the branch number you want to checkout (1-{len(branches)}): "))
                        if 1 <= branch_num <= len(branches):
                            branch_name = branches[branch_num - 1].strip()
                            # Normalize branch name by removing unwanted prefixes like 'remotes/origin/'
                            normalized_branch = branch_name.replace("remotes/origin/", "").strip()
                            checkout_branch(clone_path, normalized_branch)
                        else:
                            print("Invalid branch number.")
                    elif action == 'new':
                        new_branch_name = input("Enter the name of the new branch: ").strip()
                        try:
                            subprocess.run(['git', '-C', clone_path, 'checkout', '-b', new_branch_name], check=True)
                            print(f"Created and switched to new branch '{new_branch_name}'.")
                            push_branch(clone_path, new_branch_name)
                        except subprocess.CalledProcessError as e:
                            print(f"Error creating new branch '{new_branch_name}': {e}")
                else:
                    print("No branches found.")


            elif action == "open_file":
                file_name = input("Enter the name of the file you want to open (including extension): ")

                # Find the file in the repository (including subdirectories)
                file_path = find_file_in_repo(clone_path, file_name)

                if file_path:
                    print(f"Opening file {file_path} in VSCode...")
                    open_in_vscode(file_path)
                else:
                    # File not found, ask to create
                    create_file = input(f"File {file_name} not found in the repository at {clone_path}. Do you want to create the file? (yes/no): ").lower()
                    if create_file == 'yes':
                        file_path = os.path.join(clone_path, file_name)  # Assume creation in the root folder
                        open(file_path, 'w').close()  # Create an empty file
                        print(f"File {file_name} created.")
                        open_in_vscode(file_path)
                    else:
                        print("Operation canceled. Exiting.")

            
            elif action == "commit_changes":
                file_name = input("Enter the name of the file you want to open (including extension): ")
                file_path = find_file_in_repo(clone_path, file_name)

                if file_path:
                    print(f"Opening file {file_path} in VSCode...")
                    open_in_vscode(file_path)

                    # Prompt the user to make changes
                    input("Edit the file in VSCode, save changes, and press Enter to continue...")

                    # Check if there are changes to commit
                    try:
                        result = subprocess.run(
                            ['git', '-C', clone_path, 'status', '--porcelain'],
                            stdout=subprocess.PIPE,
                            text=True,
                            check=True
                        )
                        if not result.stdout.strip():
                            print("Make changes and commit, don't commit without changing.")
                            return

                        # If changes are present, proceed to commit and push
                        commit_message = input("Enter commit message for your changes: ")
                        subprocess.run(['git', '-C', clone_path, 'add', file_path], check=True)
                        subprocess.run(['git', '-C', clone_path, 'commit', '-m', commit_message], check=True)
                        subprocess.run(['git', '-C', clone_path, 'push'], check=True)
                        print("Changes pushed to the remote repository successfully.")
                    except subprocess.CalledProcessError as e:
                        print(f"Error processing Git operations: {e}")
                        return
                else:
                    create_file = input(f"File {file_name} not found in the repository at {clone_path}. Do you want to create the file? (yes/no): ").lower()
                    if create_file == 'yes':
                        file_path = os.path.join(clone_path, file_name)
                        open(file_path, 'w').close()
                        print(f"File {file_name} created.")
                        open_in_vscode(file_path)
                    else:
                        print("Operation canceled. Exiting.")



            elif action == "lpar_list":
                ssh_config = load_config("timeout_dynamic.yaml")
                config_path = "application_details.yaml"  # Use the file path here
                config = load_config(config_path)  # Load the configuration as a dictionary

                if config is None:
                    print("Error loading configuration.")
                    return

                git_url = config['repositories']['git_url']

                current_dir = os.path.dirname(os.path.abspath(__file__))

                # Get workspace path from user or use the default path
                workspace_path = input("Enter the VS Code workspace path (press enter to use the current directory): ") or current_dir

                # Get repository name from user input
                repo_name = input("Enter the repository name: ")

                # Construct the full repository URL
                repo_url = f"{git_url}/{repo_name}.git"

                # Clone path
                clone_path = os.path.join(workspace_path, repo_name)

                lpar_list = list(ssh_config.keys())
                print("Available Mainframe LPARs:")
                for idx, lpar in enumerate(lpar_list):
                    print(f"{idx + 1}. {lpar}")

                selected_idx = int(input("Select your target LPAR by number: ")) - 1
                selected_lpar = lpar_list[selected_idx]
                lpar_details = ssh_config[selected_lpar]

                app_list = [config['repositories']['git_Application']]
                print("Available applications:")
                for idx, app in enumerate(app_list):
                    print(f"{idx + 1}. {app}")

                app_idx = int(input("Select your application by number: ")) - 1
                application_name = app_list[app_idx]
                main_build_branch = config['repositories']['main_build_branch']

                hostname = lpar_details.get('mfip')
                port = int(lpar_details.get('sshport', 22))
                username = input("Enter your username: ")
                password = getpass("Enter your password: ")

                hlq = input("Enter your HLQ: ")
                #filename = input("Enter the filename: ")

                ssh_client, mainframe_pwd = create_ssh_connection(hostname, port, username, password)

                if ssh_client and mainframe_pwd:
                    sftp = ssh_client.open_sftp()  # Open SFTP connection
                    try:
                        # Dynamically create workspace and output directories
                        #workspace_name = "workspace"  # Default workspace name
                        workspace_name = "sandbox1"
                        outdir = f"{mainframe_pwd}/outdir"
                        workspace_path, application_path = check_and_create_directories(
                            ssh_client, mainframe_pwd, application_name, workspace_name
                        )

                        if workspace_path and application_path:
                            # Clone the latest changes from GitHub to the mainframe
                            print("Cloning the repository from GitHub to the mainframe...")
                            check_or_clone_repository(ssh_client, repo_url, application_path)

                            #change_to_git_repo(ssh_client, application_path)
                            #git_pull_and_checkout(ssh_client, application_path, main_build_branch)

                            # Search for Source File
                            filename = input("Enter the filename: ")
                            file_path = find_source_file(ssh_client, application_path, filename)

                            if file_path:
                                # Run the Build Command
                                output, error_output = run_mainframe_commands(
                                    ssh_client, hlq, application_name, filename, file_path, lpar_details, workspace_path, outdir
                                )
                                analyze_build_logs(output, error_output)
                    finally:
                        sftp.close()  # Close SFTP connection
                        ssh_client.close()



def main():
    config_path = os.path.join(os.getcwd(), 'pull_clone.yaml')

    while True:
        try:
            user_query = input("Enter your query :")
            response = requests.post(SERVER_URL, json={"query": user_query})
            if response.status_code == 200:
                action = response.json().get("action")
                handle_server_command(action, config_path)
            else:
                print(f"Server returned an error: {response.status_code}")
        except Exception as e:
            print(f"Error connecting to the server: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()




"""


open_vscode

check_internet

install_extensions

clone

list_branches

checkout_branch

open_file

commit_changes

lpar_list

----------------------------------------------
MortgageApplication

hello.cbl

"""
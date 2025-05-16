import os
import subprocess
import argparse
from datetime import datetime

def log_to_file(message, LOG_FILE):
    """Logs a message to the log file with a timestamp."""
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {message}\n")
        log_file.write("-" * 40 + "\n")  # Separator for readability

def find_file_in_repo(repo_path, file_name, LOG_FILE):
    """Search for the file in the repository folder and subfolders."""
    log_to_file(f"Searching for file '{file_name}' in repository '{repo_path}'", LOG_FILE)
    for root, _, files in os.walk(repo_path):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            log_to_file(f"File found: {file_path}", LOG_FILE)
            return file_path
    log_to_file(f"File '{file_name}' not found in repository '{repo_path}'", LOG_FILE)
    return None

def ensure_on_branch(clone_path, LOG_FILE):
    """Ensure the repository is on a valid branch."""
    try:
        result = subprocess.run(
            ['git', '-C', clone_path, 'symbolic-ref', '--short', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        current_branch = result.stdout.strip()
        log_to_file(f"Currently on branch: {current_branch}", LOG_FILE)
        return current_branch
    except subprocess.CalledProcessError:
        log_to_file("Repository is in a detached HEAD state.", LOG_FILE)
        print("Repository is in a detached HEAD state. Creating a new branch...")
        new_branch = "fix-detached-head"
        subprocess.run(['git', '-C', clone_path, 'checkout', '-b', new_branch], check=True)
        log_to_file(f"Switched to a new branch: {new_branch}", LOG_FILE)
        print(f"Switched to a new branch: {new_branch}")
        return new_branch

def main(repo_name, base_url, file_name, commit_message, active_folder_path):
    """Main function to clone the repo, find or create the file, and open it."""
    LOG_FILE = os.path.join(active_folder_path, "internet_connection_log.txt")

    #repo_url = f"{base_url}/{repo_name}.git"
    repo_url = f"{base_url}/{repo_name}.git"

    base_name = repo_name.split("/")[0]
    repo_name = repo_name.split("/")[-1]

    base_url = f'{base_url}/{base_name}/'

    print(f'\n{repo_url}')
    clone_path = os.path.join(os.getcwd(), repo_name)  ##### check
    print(f'\n{clone_path}')

    log_to_file(f"Starting process for repository: {repo_name}", LOG_FILE)

    if not os.path.exists(clone_path):
        log_to_file(f"Cloning repository from {repo_url} to {clone_path}", LOG_FILE)
        print(f"Cloning repository {repo_name}...")
        subprocess.run(["git", "clone", repo_url, clone_path], check=True)
        log_to_file(f"Repository cloned successfully", LOG_FILE)
    else:
        log_to_file(f"Repository {repo_name} already exists at {clone_path}", LOG_FILE)
        print(f"Repository {repo_name} already exists.")

    file_path = find_file_in_repo(clone_path, file_name, LOG_FILE)

    if file_path:
        log_to_file(f"File {file_name} found in repository", LOG_FILE)
        print(f"File {file_name} found in the repository.")
    else:
        file_path = os.path.join(clone_path, file_name)
        open(file_path, 'w').close()
        log_to_file(f"File {file_name} not found. Created new file at {file_path}", LOG_FILE)
        print(f"File {file_name} not found in the repository. Created new file at: {file_path}")

    # Ensure we are on a valid branch
    current_branch = ensure_on_branch(clone_path, LOG_FILE)

    try:
        log_to_file("Checking for untracked files", LOG_FILE)
        result = subprocess.run(['git', '-C', clone_path, 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
        if result.stdout.strip():
            log_to_file("Staging all changes", LOG_FILE)
            subprocess.run(['git', '-C', clone_path, 'add', '.'], check=True)
        else:
            log_to_file("No changes to stage", LOG_FILE)
            print("No changes detected. Please make changes before committing.")
            return

        log_to_file("Staging and committing changes", LOG_FILE)
        subprocess.run(['git', '-C', clone_path, 'commit', '-m', commit_message], check=True)
        log_to_file(f"Committing changes with message: {commit_message}", LOG_FILE)

        log_to_file("Pushing changes to the remote repository", LOG_FILE)
        subprocess.run(['git', '-C', clone_path, 'push', 'origin', current_branch], check=True)
        log_to_file("Changes pushed to the remote repository successfully", LOG_FILE)
        print("Changes pushed to the remote repository successfully.")
    except subprocess.CalledProcessError as e:
        log_to_file(f"Error during Git operations: {e}", LOG_FILE)
        print(f"Error processing Git operations: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process repository name, base URL, file name, and commit message.")
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    parser.add_argument("file_name", type=str, help="The name of the file to open or create")
    parser.add_argument("commit_message", type=str, help="The commit message for changes")
    parser.add_argument("active_folder_path", type=str, help="The path of the active workspace folder")
    args = parser.parse_args()

    main(args.repo_name, args.base_url, args.file_name, args.commit_message, args.active_folder_path)



# python3 commit_after_change_log.py MortgageApplication https://github.com/gmsadmin-git hello.cbl frontEnd /Users/thrisham/Desktop/cobol_code/mainframe_final

#python3 commit_after_change_log.py MortgageApplication https://github.com/Thrisha020/ hello.cbl frontEnd /Users/thrisham/Desktop/cobol_code/mainframe_final


#  python3 commit_after_change_log.py MortgageApplication https://github.com/gmsadmin-git hello.cbl frontEnd /Users/thrisham/Desktop/cobol_code/mainframe_final

#  python3 commit_after_change_log.py gmsadmin-git/MortgageApplication https://github.com hello.cbl changedd /Users/thrisham/Desktop/cobol_code/mainframe_final

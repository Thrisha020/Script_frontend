import os
import subprocess
import requests
import time
import yaml
import shutil

import platform
import os
import webbrowser
import shutil
import paramiko
from getpass import getpass
import subprocess

import argparse

# def load_config(yaml_file):  # Default file name
#     script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the directory of the running script
#     yaml_path = os.path.join(script_dir, yaml_file)  # Construct the full path to the YAML file
#     if os.path.exists(yaml_path):
#         with open(yaml_path, 'r') as file:
#             config = yaml.safe_load(file)
#         return config
#     else:
#         raise FileNotFoundError(f"Configuration file '{yaml_file}' not found at path: {yaml_path}")

# def clone_repo(repo_url, clone_path):
#     try:
#         subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
#         return f"Repository cloned successfully to {clone_path}."
#     except subprocess.CalledProcessError as e:
#         return f"Error cloning repository: {e}"


import subprocess

def clone_repo(repo_url, clone_path, branch='Feature/Demo'):
    try:
        subprocess.run(['git', 'clone', '-b', branch, repo_url, clone_path], check=True)
        return f"Repository cloned successfully from '{branch}' branch to {clone_path}."
    except subprocess.CalledProcessError as e:
        return f"Error cloning repository from '{branch}' branch: {e}"


def is_git_repo(folder_path):
    return os.path.isdir(os.path.join(folder_path, ".git"))

def pull_latest_changes(repo_path):
    try:
        subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
        return "Latest changes pulled successfully."
    except subprocess.CalledProcessError as e:
        return f"Error pulling latest changes: {e}"

def delete_folder(folder_path):
    permission = input(f"The folder '{folder_path}' is not a git repository. Do you want to delete it? (yes/no): ").lower()
    if permission == 'yes':
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' deleted.")
        return True
    else:
        print("Operation canceled. Exiting.")
        return False


def main(repo_name,base_url):


            workspace_path = os.getcwd()
            #repo_name = input("Enter the repository name: ")
            repo_url = f"{base_url}/{repo_name}.git"
            clone_path = os.path.join(workspace_path, repo_name)

            #if action == "clone":
            if not os.path.isdir(clone_path):
                #print(f"Cloning repository from {repo_url} to {clone_path}...")
                return clone_repo(repo_url, clone_path)
                
                # Verify if the folder is a Git repository
            if is_git_repo(clone_path):
                #print(f"Repository already cloned at {clone_path}. Pulling latest changes...")
                return pull_latest_changes(clone_path)
            else:
                    # Ask for permission to delete the folder
                if delete_folder(clone_path):
                    #print(f"Re-cloning repository from {repo_url} to {clone_path}...")
                    return clone_repo(repo_url, clone_path)
                else:
                        return
                
#main('MortgageApplication','url')
#print("----------------------------------")




if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Process repository name and base URL.")
    
    # Add arguments for repo_name and base_url
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Call the main function with the provided arguments
    print(main(args.repo_name, args.base_url))


# python3 clone.py MortgageApplication https://github.com/gmsadmin-git


#https://github.com/gmsadmin-git
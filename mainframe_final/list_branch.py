import subprocess
import os
import yaml
import argparse


def is_git_repo(folder_path):
    return os.path.isdir(os.path.join(folder_path, ".git"))


def list_branches(repo_path):
    """List all available branches in the repository."""
    try:
        result = subprocess.run(['git', '-C', repo_path, 'branch', '-a'], check=True, text=True, capture_output=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error listing branches: {e}")
        return []



def main(repo_name, base_url):
    workspace_path = os.getcwd()
    #repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(workspace_path, repo_name)

    if not is_git_repo(clone_path):
        return f"Error: {clone_path} is not a valid Git repository."
    
    branches = list_branches(clone_path)
    if branches:
        #print("Available branches:")
        return branches
        # for i, branch in enumerate(branches, start=1):
        #     print(f"{i}. {branch}")
            # You can add logic here to ask the user for further branch operations

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

### 1 follow-up question: Enter the repo name:

# python3 list_branch.py MortgageApplication https://github.com/gmsadmin-git

#remotes/origin/feature/test
    
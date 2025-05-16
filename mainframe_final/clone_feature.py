import subprocess

def clone_repository():
    # Ask the user for the repository URL
    repo_url = input("Enter the repository URL: ")
    
    # Ask the user for the feature branch they want to clone
    feature_branch = input("Enter the feature branch name: ")
    
    # Define the directory where the repository will be cloned
    clone_dir = input("Enter the directory to clone into (leave blank for current directory): ")
    
    if clone_dir.strip() == "":
        clone_dir = None  # Clone into current directory
    
    try:
        # Clone the repository
        print(f"Cloning repository from branch: {feature_branch}")
        
        # Use the git command to clone the specific branch
        clone_command = ['git', 'clone', '--branch', feature_branch, repo_url]
        
        if clone_dir:
            clone_command.append(clone_dir)
        
        # Execute the command
        subprocess.run(clone_command, check=True)
        
        print(f"Repository cloned successfully from branch '{feature_branch}'!")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while cloning the repository: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    clone_repository()
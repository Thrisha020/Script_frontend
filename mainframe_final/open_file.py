import os
import subprocess                
import argparse

def find_file_in_repo(repo_path, file_name):
    for root, dirs, files in os.walk(repo_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def open_in_vscode(file_path):
    try:
        subprocess.run(["code", file_path], check=True)
        #print(f"File opened")
        return f"File opened"
    except FileNotFoundError:
        #print("VSCode is not installed. Please install VSCode from https://code.visualstudio.com/")
        return f"VSCode is not installed. Please install VSCode from https://code.visualstudio.com/"
    except subprocess.CalledProcessError as e:
        return f"Error opening file in VSCode: {e}"
        #print(f"Error opening file in VSCode: {e}")



def main(repo_name, base_url,file_name):
    workspace_path = os.getcwd()
    repo_url = f"{base_url}/{repo_name}.git"
    clone_path = os.path.join(workspace_path, repo_name)

    #file_name = input("Enter the name of the file you want to open (including extension): ")

    # Find the file in the repository (including subdirectories)
    file_path = find_file_in_repo(clone_path, file_name)

    if file_path:
        print(f"Opening file {file_path} in VSCode...")
        if open_in_vscode(file_path) == 'File opened':
            print('Successfully openned')

    else:
        print('create_new_file')
    # else:
    #     create_file = input(f"File {file_name} not found in the repository at {clone_path}. Do you want to create the file? (yes/no): ").lower()
    #     if create_file == 'yes':
    #         file_path = os.path.join(clone_path, file_name)  # Assume creation in the root folder
    #         open(file_path, 'w').close()  # Create an empty file
    #         print(f"File {file_name} created.")
    #         open_in_vscode(file_path)
    #     else:
    #         print("Operation canceled. Exiting.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process repository name and base URL.")
    parser.add_argument("repo_name", type=str, help="The name of the repository to process")
    parser.add_argument("base_url", type=str, help="The base URL of the repository")
    parser.add_argument("file_name", type=str, help="The name of the file which is to open")
    args = parser.parse_args()

    main(args.repo_name, args.base_url, args.file_name)

### 1 follow-up question: Enter the repo name:
### 2 follow-up question: Enter the name of the file you want to open (including extension):  --> file_name

# python3 open_file.py MortgageApplication https://github.com/gmsadmin-git hello.cbl



#https://github.com/gmsadmin-git
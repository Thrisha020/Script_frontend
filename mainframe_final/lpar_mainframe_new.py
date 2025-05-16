"""
Author : Thrisha

date : 13th feb

"""


import os, json
from getpass import getpass
import webbrowser
import shutil
import paramiko
import yaml
import argparse
from datetime import datetime


def log_to_file(message, LOG_FILE):
    """Logs a message to the log file with a timestamp."""
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - {message}\n")
        log_file.write("-" * 40 + "\n")  # Separator for readability


def load_config(yaml_file):  # Default file name
    script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the directory of the running script
    yaml_path = os.path.join(script_dir, yaml_file)  # Construct the full path to the YAML file
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    else:
        raise FileNotFoundError(f"Configuration file '{yaml_file}' not found at path: {yaml_path}")

def create_ssh_connection(hostname, port, username, password,LOG_FILE):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname, port=port, username=username, password=password)
        log_to_file("Connection successful!",LOG_FILE)


        command = "cd /u/gmszfs && pwd"
        stdin, stdout, stderr = ssh.exec_command(command)
        mainframe_pwd = stdout.read().decode().strip()
        # stdin, stdout, stderr = ssh.exec_command("pwd")
        # mainframe_pwd = stdout.read().decode().strip()
        log_to_file(f"Mainframe working directory: {mainframe_pwd}",LOG_FILE)


        print("Connection successful!")
        print(f"Mainframe working directory: {mainframe_pwd}")
        return ssh, mainframe_pwd
    except Exception as e:

        log_to_file(f"SSH connection failed: {e}",LOG_FILE)
        print(f"SSH connection failed: {e}") 
        return f"SSH connection failed: {e}",None



def check_and_create_directories(ssh, mainframe_pwd, application, LOG_FILE,workspace_name="sandbox"):
    try:
        # Dynamically construct paths
        workspace_path = f"{mainframe_pwd}/{workspace_name}"
        application_path = f"{workspace_path}/{application}"

        # Ensure workspace directory exists
        
        log_to_file(f"Ensuring workspace directory: {workspace_path}",LOG_FILE)
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {workspace_path}")
        if stderr.read().strip():
            raise Exception(f"Failed to create workspace directory: {workspace_path}")

        # Ensure application directory exists
        log_to_file(f"Ensuring application directory: {application_path}",LOG_FILE)
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {application_path}")
        if stderr.read().strip():
            raise Exception(f"Failed to create application directory: {application_path}")

        return workspace_path, application_path
    except Exception as e:
        log_to_file(f"Error creating directories: {e}",LOG_FILE)
        return None, None


def check_or_clone_repository(ssh, repo_url, application_path,LOG_FILE):
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
            #print(f"No Git repository found at {application_path}. Cloning the repository...")
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
            log_to_file("Repository cloned successfully.",LOG_FILE)
            print(f"Repository cloned successfully.")
            return
        else:
            log_to_file(f"Repository already exists at {application_path}. Pulling latest changes...",LOG_FILE)
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
            log_to_file("Latest changes pulled successfully.",LOG_FILE)
            print(f"Latest changes pulled successfully.")
            return
    except Exception as e:
        log_to_file(f"Error during repository setup: {e}",LOG_FILE)    



# Search for the Absolute Path of the Source File Dynamically
def find_source_file(ssh, application_path, filename,LOG_FILE):
    try:
        log_to_file(f"Searching for '{filename}' in '{application_path}'...",LOG_FILE)

        # Case-sensitive search using `-name`
        find_command = f"find {application_path} -type f -name \"{filename}\""
        log_to_file(f"Executing: {find_command}",LOG_FILE)

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
        return 
    

# Run mainframe commands and log messages to a file
def run_mainframe_commands_1(ssh, hlq, application, filename, file_path, config, workspace, outdir, LOG_FILE):
    try:
        folder_name = os.path.dirname(file_path) if file_path else ""
        
        if not folder_name:
            raise ValueError("Cannot determine the folder name. The source file path is invalid.")
        
        log_to_file(f"Ensuring output directory exists: {outdir}",LOG_FILE)
        ssh.exec_command(f"mkdir -p {outdir}")
        
        groovyzpath = config.get('groovyzpath')
        zappbuildpath = config.get('zappbuildpath')
        
        if not groovyzpath or not zappbuildpath:
            raise ValueError("Missing groovyzpath or zappbuildpath in configuration.")
        
        # Construct the command
        uss_command = (
            f". ~/.profile && "
            f"{groovyzpath} "
            f"-DBB_DAEMON_HOST 127.0.0.1 -DBB_DAEMON_PORT 7380 "
            f"{zappbuildpath} "
            f"--sourceDir {workspace} "
            f"--workDir {outdir} "
            f"--hlq {hlq} "
            f"--application {application} "
            f"{application}/cobol/{filename} "
        )

# Executing USS Command: /u/gmszfs/dbb20/usr/lpp/IBM/dbb/bin/groovyz -DBB_PERSONAL_DAEMON /u/gmsratn/zAppbuild20/Development/build.groovy 
# --workspace /u/gmsratn/workspace --application MortgageApplication --outDir /u/gmsratn/outdir 
# --hlq GMSRATN /u/gmsratn/workspace/MortgageApplication/cobol/hello.cbl --verbose
        log_to_file(f"Executing USS Command: {uss_command}",LOG_FILE)
        
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
        return 

def run_mainframe_commands(ssh, hlq, application, filename, file_path, lpar_details, workspace, outdir, LOG_FILE):
    try:
        folder_name = os.path.dirname(file_path) if file_path else ""
        
        if not folder_name:
            raise ValueError("Cannot determine the folder name. The source file path is invalid.")
        
        log_to_file(f"Ensuring output directory exists: {outdir}", LOG_FILE)
        ssh.exec_command(f"mkdir -p {outdir}")
        
        # Extract configuration details correctly
        config = list(lpar_details.values())[0]  # Get the first dictionary inside lpar_details
        
        groovyzpath = config.get('groovyzpath')
        zappbuildpath = config.get('zappbuildpath')
        
        if not groovyzpath or not zappbuildpath:
            raise ValueError("Missing groovyzpath or zappbuildpath in configuration.")
        
        # Construct the command
        uss_command = (
            f". ~/.profile && "
            f"{groovyzpath} "
            f"-DBB_DAEMON_HOST 127.0.0.1 -DBB_DAEMON_PORT 7380 "
            f"{zappbuildpath} "
            f"--sourceDir {workspace} "
            f"--workDir {outdir} "
            f"--hlq {hlq} "
            f"--application {application} "
            f"{application}/cobol/{filename} "
        )

        log_to_file(f"Executing USS Command: {uss_command}", LOG_FILE)
        
        # Execute the command and stream output
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

        print(f'Command output (stdout):    {"\n".join(stdout_output)}')
        print(f'Command error output (stderr):    {"\n".join(stderr_output)}')
        return "\n".join(stdout_output), "\n".join(stderr_output)
    
    except Exception as e:
        error_message = f"Failed to execute build command: {e}"
        log_to_file(error_message, LOG_FILE)
        print(error_message)
        return "", error_message  # Return empty output and error string instead of None


# Analyze Logs and Display Build Status
def analyze_build_logs(output, error_output,LOG_FILE):
    if error_output:

        log_to_file("Build failed.",LOG_FILE)
        print(f"Error Logs:\n{error_output}")
        return
    else:
        log_to_file("Build succeeded.",LOG_FILE)
        print(f"Build Output:\n{output}")
        return



def main(repo_name, git_url, username, password , hlq ,filename, lpar_details,active_folder_path):
    # ssh_config = load_config("timeout_dynamic.yaml")
    # config_path = "application_details.yaml"
    # config = load_config(config_path)
   
    # if config is None:
    #     print("Error loading configuration.")
    #     return

    #current_dir = os.path.dirname(os.path.abspath(__file__))
    #workspace_path = input("Enter the VS Code workspace path (press enter to use the current directory): ") or current_dir
    #clone_path = os.path.join(workspace_path, repo_name)
    # LOG_FILE = os.path.join(active_folder_path, "internet_connection_log.txt")
    # repo_url = f"{git_url}/{repo_name}.git"

    LOG_FILE = os.path.join(active_folder_path, "internet_connection_log.txt")

    
    repo_url = f"{git_url}/{repo_name}.git"

    



    # lpar_list = list(ssh_config.keys())
    # print("Available Mainframe LPARs:")
    # for idx, lpar in enumerate(lpar_list):
    #     print(f"{idx + 1}. {lpar}")

    # selected_idx = int(input("Select your target LPAR by number: ")) - 1
    # selected_lpar = lpar_list[selected_idx]
    # lpar_details = ssh_config[selected_lpar]

    # app_list = [config['repositories']['git_Application']]
    # print("Available applications:")
    # for idx, app in enumerate(app_list):
    #     print(f"{idx + 1}. {app}")

    # app_idx = int(input("Select your application by number: ")) - 1
    # application_name = app_list[app_idx]
    # main_build_branch = config['repositories']['main_build_branch']
    lpar_details = json.loads(lpar_details)
    lpar_values = list(lpar_details.values())[0]
##########

    # lpar_details = json.loads(lpar_details)
    # lpar_values = lpar_details.values()
    # data_list = list(lpar_values)

# Access the first dictionary in the list
    #first_dict = data_list[0]
          #hostname = first_dict.get('mfip')
    # print(hostname)
    # print(type(hostname))
    
       #port = int(first_dict.get('sshport', 22))
    # print(port)
    # print(type(port))
    #username = input("Enter your username: ")
    #password = getpass("Enter your password: ")
    #hlq = input("Enter your HLQ: ")

        #ssh_client, mainframe_pwd = create_ssh_connection('13.233.106.52', '2022', username, password, LOG_FILE)


    hostname = lpar_values.get('mfip')
    port = int(lpar_values.get('sshport', 22))

    ssh_client, mainframe_pwd = create_ssh_connection(hostname, port, username, password, LOG_FILE)

    if ssh_client and mainframe_pwd:
        sftp = ssh_client.open_sftp()
        try:
            workspace_name = "sandbox"
            outdir = f"{mainframe_pwd}/outdir"
            workspace_path, application_path = check_and_create_directories(
                ssh_client, mainframe_pwd, repo_name,LOG_FILE, workspace_name
            )

            if workspace_path and application_path:
                print("Cloning the repository from GitHub to the mainframe...")
                check_or_clone_repository(ssh_client, repo_url, application_path, LOG_FILE)

                #filename = input("Enter the filename: ")
                file_path = find_source_file(ssh_client, application_path, filename,LOG_FILE)

                if file_path:
                    output, error_output = run_mainframe_commands(
                        ssh_client, hlq, repo_name, filename, file_path, lpar_details, workspace_path, outdir,LOG_FILE
                    )
                    analyze_build_logs(output, error_output,LOG_FILE)
                    print(f'\nCommand output (stdout): \n{output}')
                    print(f'\nCommand error output (stderr): \n{error_output}')
                    return
        finally:
            sftp.close()
            ssh_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mainframe Git repository processing.")
    parser.add_argument("repo_name", type=str, help="The name of the repository")
    parser.add_argument("base_url", type=str, help="The Git base URL")
    parser.add_argument("username", type=str, help="username to login into the mainframe")
    parser.add_argument("password", type=str, help="password to login into the mainframe")
    parser.add_argument("hlq", type=str, help="hlq to login into the mainframe")
    parser.add_argument("filename", type=str, help="Filename to execute the uss command")
    parser.add_argument("lpar_details", type=str, help="Get the the path to run USSz")
    parser.add_argument("active_folder_path", type=str, help="The path of the active workspace folder")
    args = parser.parse_args()

    main(args.repo_name, args.base_url,args.username, args.password , args.hlq , args.filename , args.lpar_details, args.active_folder_path)


#   python3 lpar_mainframe_log.py MortgageApplication https://github.com/gmsadmin-git adcdmst sys3 ADCDMST.MORTGAGE hello.cbl '{"gmsmf": {"mfip": "13.233.165.158", "sshport": "2022", "groovyzpath": "/usr/lpp/IBM/dbb/bin/groovyz", "zappbuildpath": "/tmp/ibmzappbuild/dbb-zappbuild/build.groovy"}}' /Users/thrisham/Desktop/cobol_code/mainframe_final


#   python3 lpar_mainframe_new.py gmsadmin-git/MortgageApplication https://github.com adcdmst sys3 ADCDMST.MORTGAGE hello.cbl '{"gmsmf": {"mfip": "13.233.165.158", "sshport": "2022", "groovyzpath": "/usr/lpp/IBM/dbb/bin/groovyz", "zappbuildpath": "/tmp/ibmzappbuild/dbb-zappbuild/build.groovy"}}' /Users/thrisham/Desktop/cobol_code/mainframe_final
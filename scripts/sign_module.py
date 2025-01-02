import os
import sys
import subprocess

def read_nossign_file(nossign_file_path):
    """Reads file paths from a .nossign file, converting relative paths to absolute paths."""
    
    if not os.path.exists(nossign_file_path):
        print(f"Error: The .nossign file does not exist {nossign_file_path}")
        sys.exit(1)
    
    # Get the directory of the .nossign file
    nossign_dir = os.path.dirname(nossign_file_path)
    
    with open(nossign_file_path, 'r') as nossign_file:
        # Read file paths, converting relative paths to absolute paths
        return [
            os.path.abspath(os.path.join(nossign_dir, line.strip())) if not os.path.isabs(line.strip()) else line.strip()
            for line in nossign_file.readlines() if line.strip()
        ]


def run_powershell_script(file_path):
    """Runs the PowerShell script with the given file path. Converts relative paths to absolute and checks if they exist."""
    # Ensure the PowerShell script exists
    script_path = 'sign_nodos.ps1'
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found.")
        sys.exit(1)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return  # Skip this file if it doesn't exist

    # Prepare the PowerShell command to call the script
    command = ["powershell", "-ExecutionPolicy", "ByPass", "-File", script_path, file_path]

    try:
        # Run the PowerShell script and capture output and error
        result = subprocess.run(command, check=True, capture_output=True, text=True)

        # Check the result
        if result.returncode == 0:
            print(f"Successfully signed: {file_path}")
            print(f"Output: {result.stdout}")
        else:
            print(f"Error signing {file_path}. Exit Code: {result.returncode}")
            print(f"Error Output: {result.stderr}")
            exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error during signing process for {file_path}: {e}")
        print(f"Error Output: {e.stderr}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

def find_nossign_files(directory):
    # List to store the paths of all .nossign files
    nossign_files = []
    
    # Traverse the directory and its subfolders
    for root, dirs, files in os.walk(directory):
        # For each file in the current directory
        for file in files:
            if file.endswith('.nossign'):
                # Construct the full path to the file
                file_path = os.path.join(root, file)
                nossign_files.append(file_path)
    
    if(nossign_files.__len__()):
        return nossign_files
    else:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)

    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: The specified path {directory} is not a directory.")
        sys.exit(1)

    nossign_files = find_nossign_files(directory)
    if nossign_files == None:
        print("No .nossign files found.")
        exit(1)

    # Read paths from the .nossign file
    file_paths = []
    for nossign_file in nossign_files:
        file_paths.extend(read_nossign_file(nossign_file))

    # Call the PowerShell script for each file path
    for file_path in file_paths:
        run_powershell_script(file_path)

if __name__ == "__main__":
    main()
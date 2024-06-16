import os
import subprocess

def run_program(program_path):
    try:
        subprocess.run(["python", program_path], check=True)
        print(f"Program '{program_path}' executed successfully!")
        return True
    except subprocess.CalledProcessError:
        print(f"Error executing program '{program_path}'!")
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    program_dir = os.path.join(script_dir, 'pypgrms')

    # Ensure required directories exist
    required_dirs = ['codes', 'pseudo', 'flowcharts']
    for req_dir in required_dirs:
        dir_path = os.path.join(script_dir, req_dir)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Ensured directory exists: {dir_path}")

    program_files = [
        file for file in os.listdir(program_dir) if file.endswith(".py")
    ]

    for program_file in program_files:
        program_path = os.path.join(program_dir, program_file)
        print(f"Running program: {program_path}")
        if run_program(program_path):
            continue
        else:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()

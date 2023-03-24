import argparse, os


def read_file_lines(filepath):
    with open(filepath, "r") as fd:
        return fd.read().splitlines()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to fix broken symbolic links in modules path (coded by @secu_x11)")
    parser.add_argument("--modules-path", action='store', required=True, help="Modules path")
    args = parser.parse_args()

    if not os.path.isdir(args.modules_path):
        print(f"Modules path: '{args.modules_path}' not exists or is not a directory")
        exit(1)

    for command_folder in os.scandir(args.modules_path):
        if not os.path.isdir(command_folder):
            continue

        if command_folder.name == "__pycache__":
            continue

        print(f"[+] Enter in folder: '{command_folder.name}'")
        
        command_files = os.listdir(command_folder)
        for command_file in command_files:
            command_file_path = os.path.join(command_folder,command_file)
            command_file_lines = read_file_lines(command_file_path)
            if len(command_file_lines) != 1:
                continue

            filename_target_link = command_file_lines[0]
            filepath_target_link = os.path.join(command_folder, filename_target_link)
            if not os.path.isfile(filepath_target_link):
                print(f"[!] Broken symbolic link file: '{command_file_path}' points to non-existent file: '{filepath_target_link}'")
                continue
            
            print(f"  [+] Creating Symbolic Link: '{command_file_path}' -> '{filepath_target_link}'")
            os.remove(command_file_path)
            os.symlink(os.path.basename(filepath_target_link), command_file_path)

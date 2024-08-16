import time
import argparse

def follow(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1) 
                continue
            print(line, end='')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Follow the log file.')
    parser.add_argument('file_path', type=str, help='Path to the log file')
    args = parser.parse_args()

    follow(args.file_path)
    
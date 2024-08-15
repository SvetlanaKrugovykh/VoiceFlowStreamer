import time

def follow(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file.seek(0, 2)  # Перемещаем указатель в конец файла
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)  # Ждем, если нет новых строк
                continue
            print(line, end='')

if __name__ == "__main__":
    log_file_path = 'transcriptions.log'
    follow(log_file_path)
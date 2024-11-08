import os
import tarfile
import sys
import shutil
import re

class ShellEmulator:
    def __init__(self, user_name, host_name, tar_path):
        self.user_name = user_name
        self.host_name = host_name
        self.virtual_fs_root = '/tmp/virtual_fs'
        self.current_path = self.virtual_fs_root
        
        # Распаковка виртуальной файловой системы
        self.extract_tar(tar_path)

    def extract_tar(self, tar_path):
        """Извлекает содержимое tar архива в виртуальную файловую систему"""
        if os.path.exists(self.virtual_fs_root):
            shutil.rmtree(self.virtual_fs_root)
        os.makedirs(self.virtual_fs_root)

        with tarfile.open(tar_path, "r") as tar:
            tar.extractall(self.virtual_fs_root, filter=lambda x, _: x)


    def run(self):
        """Основной цикл выполнения команд"""
        while True:
            command = input(f'{self.user_name}@{self.host_name}:{self.current_path}$ ').strip()
            if command == 'exit':
                print("Выход из эмулятора.")
                break
            elif command.startswith('ls'):
                self.ls()
            elif command.startswith('cd'):
                self.cd(command.split()[1] if len(command.split()) > 1 else '')
            elif command.startswith('chmod'):
                self.chmod(command)
            elif command.startswith('wc'):
                self.wc(command.split()[1] if len(command.split()) > 1 else '')
            else:
                print(f"Команда не найдена: {command}")

    def ls(self):
        """Выводит содержимое текущего каталога"""
        try:
            files = os.listdir(self.current_path)
            print("\n".join(files))
        except FileNotFoundError:
            print(f"Ошибка: Путь {self.current_path} не найден")

    def cd(self, path):
        """Изменяет текущий каталог"""
        if not path:
            self.current_path = self.virtual_fs_root
        else:
            new_path = os.path.join(self.current_path, path)
            if os.path.isdir(new_path):
                self.current_path = new_path
            else:
                print(f"Ошибка: {path} не является каталогом")

    def chmod(self, command):
        """Эмулирует изменение прав доступа к файлу"""
        parts = command.split()
        if len(parts) != 3:
            print("Использование: chmod <mode> <filename>")
            return
        
        mode = parts[1]
        filename = parts[2]
    
        # Проверяем, что mode является корректной триадой (например, '644')
        if not re.match(r"^[0-7]{3}$", mode):
            print(f"Ошибка: Неверный формат прав {mode}")
            return
        
        # Имитируем успешное изменение прав доступа
        print(f"Права доступа к файлу {filename} изменены на {mode}")
    

    def wc(self, file):
        """Подсчитывает количество строк, слов и символов в файле"""
        file_path = os.path.join(self.current_path, file)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.splitlines()
                words = content.split()
                chars = len(content)
                print(f"Строк: {len(lines)}, Слов: {len(words)}, Символов: {chars}")
        except FileNotFoundError:
            print(f"Ошибка: Файл {file} не найден")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Использование: python emulator.py <user_name> <host_name> <tar_path>")
        sys.exit(1)

    user_name = sys.argv[1]
    host_name = sys.argv[2]
    tar_path = sys.argv[3]

    emulator = ShellEmulator(user_name, host_name, tar_path)
    emulator.run()

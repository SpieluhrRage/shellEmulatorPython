import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import tarfile
from dz import ShellEmulator  # Импортируем эмулятор для тестирования

class TestShellEmulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Создаем временную файловую систему для тестов
        cls.virtual_fs_path = '/tmp/test_virtual_fs'
        os.makedirs(cls.virtual_fs_path, exist_ok=True)

        # Создаем тестовый архив tar
        cls.tar_path = '/tmp/test_vfs.tar'
        with tarfile.open(cls.tar_path, 'w') as tar:
            for i in range(0, 2):
                file_path = os.path.join(cls.virtual_fs_path, f'file{i}.txt')
                with open(file_path, 'w') as f:
                    f.write(f"File {i} contents.\n")
                tar.add(file_path, arcname=f'file{i}.txt')
        
        # Инициализация ShellEmulator с тестовыми параметрами
        cls.emulator = ShellEmulator(user_name='testuser', host_name='testhost', tar_path=cls.tar_path)

    @classmethod
    def tearDownClass(cls):
        # Удаляем временные файлы и директории после тестов
        shutil.rmtree(cls.virtual_fs_path)
        os.remove(cls.tar_path)

    def setUp(self):
        # Выполняем начальную настройку перед каждым тестом
        self.emulator.current_path = self.emulator.virtual_fs_root

    def test_ls_displays_directory_contents(self):
        # Проверяем, что ls выводит содержимое каталога
        with patch('builtins.print') as mocked_print:
            self.emulator.ls()
            mocked_print.assert_called_with("nested_directory\nroot_file.txt\ntest_directory")

    def test_ls_no_files(self):
        # Проверяем ls в пустом каталоге
        empty_dir = os.path.join(self.emulator.virtual_fs_root, 'empty_dir')
        os.makedirs(empty_dir)
        self.emulator.current_path = empty_dir
        with patch('builtins.print') as mocked_print:
            self.emulator.ls()
            mocked_print.assert_called_with('')  # Ничего не должно быть напечатано

    def test_cd_changes_directory(self):
        # Проверяем, что cd корректно меняет каталог
        sub_dir = os.path.join(self.emulator.virtual_fs_root, 'subdir')
        os.makedirs(sub_dir)
        self.emulator.cd('subdir')
        self.assertEqual(self.emulator.current_path, sub_dir)

    def test_cd_root_directory(self):
        # Проверяем, что cd без аргументов возвращает в корневой каталог
        self.emulator.current_path = os.path.join(self.emulator.virtual_fs_root, 'some_dir')
        self.emulator.cd('')
        self.assertEqual(self.emulator.current_path, self.emulator.virtual_fs_root)

    @patch("builtins.print")
    def test_chmod_correct_permissions(self, mocked_print):
        emulator = ShellEmulator("timur", "host", "newar.tar")
        emulator.chmod("chmod 644 testfile.txt")
        mocked_print.assert_called_with("Права доступа к файлу testfile.txt изменены на 644")
    
    @patch("builtins.print")
    def test_chmod_incorrect_permissions(self, mocked_print):
        emulator = ShellEmulator("timur", "host", "newar.tar")
        emulator.chmod("chmod 888 testfile.txt")
        mocked_print.assert_called_with("Ошибка: Неверный формат прав 888")

    def test_wc_counts_in_file(self):
        # Проверяем, что wc корректно подсчитывает строки, слова и символы
        with patch('builtins.print') as mocked_print:
            self.emulator.wc('root_file.txt')
            mocked_print.assert_called_with("Строк: 1, Слов: 3, Символов: 26")

    def test_wc_non_existent_file(self):
        # Проверка wc для несуществующего файла
        with patch('builtins.print') as mocked_print:
            self.emulator.wc('non_existent_file.txt')
            mocked_print.assert_called_with("Ошибка: Файл non_existent_file.txt не найден")

    @patch("builtins.print")
    def test_exit_command(self, mocked_print):
        emulator = ShellEmulator("timur", "host", "newar.tar")
        with patch("builtins.input", side_effect=["exit"]):
            emulator.run()
        mocked_print.assert_any_call("Выход из эмулятора.")


if __name__ == '__main__':
    unittest.main()

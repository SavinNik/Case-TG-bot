import unittest
from unittest.mock import patch, MagicMock
from bot import load_captions, handle_photo, share_response


class TestTelegramBot(unittest.TestCase):

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='Caption 1\nCaption 2\nCaption 3\n')
    def test_load_captions(self, mock_open):
        captions = load_captions('dummy_path')
        self.assertEqual(len(captions), 3)
        self.assertIn('Caption 1\n', captions)
        self.assertIn('Caption 2\n', captions)
        self.assertIn('Caption 3\n', captions)

    @patch('telebot.TeleBot.get_file')
    @patch('telebot.TeleBot.download_file')
    @patch('telebot.TeleBot.send_photo')
    @patch('telebot.TeleBot.send_message')
    @patch('PIL.Image.open')
    @patch('PIL.ImageDraw.Draw')
    @patch('PIL.ImageFont.truetype')
    def test_handle_photo(self, mock_truetype, mock_draw, mock_open_image, mock_send_message, mock_send_photo,
                          mock_download_file, mock_get_file):
        # Настройка мока
        mock_get_file.return_value.file_path = 'file/path'
        mock_download_file.return_value = b'test_image_data'

        # Создаем мок для объекта изображения и его метода save
        mock_image = MagicMock()
        mock_open_image.return_value = mock_image

        message = MagicMock()
        message.from_user.id = 12345
        message.chat.id = 67890
        message.photo = [MagicMock(file_id='file_id_1')]

        # Вызов тестируемой функции
        handle_photo(message)

        # Проверка вызовов
        mock_get_file.assert_called_once_with('file_id_1')
        mock_download_file.assert_called_once_with('file/path')
        mock_open_image.assert_called_once()

        # Проверяем, что метод save был вызван на объекте изображения
        mock_image.save.assert_called_once()

        mock_send_photo.assert_called_once()
        mock_send_message.assert_called_once_with(67890, "Хотите поделиться этой картинкой в нашем канале? (Да/Нет)")

    @patch('telebot.TeleBot.send_photo')
    @patch('telebot.TeleBot.send_message')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_share_response_yes(self, mock_open, mock_send_message, mock_send_photo):
        message = MagicMock()
        message.text = 'Да'
        message.from_user.id = 12345
        message.chat.id = 67890

        with patch('os.path.join', return_value='dummy_path'):
            share_response(message)

            mock_open.assert_called_once_with('dummy_path', 'rb')
            mock_send_photo.assert_called_once()
            mock_send_message.assert_called_once_with(67890, "Картинка успешно отправлена в канал!")

    @patch('telebot.TeleBot.send_message')
    def test_share_response_no(self, mock_send_message):
        message = MagicMock()
        message.text = 'Нет'
        message.chat.id = 67890

        share_response(message)

        mock_send_message.assert_called_once_with(67890, "Хорошо, картинка не будет отправлена.")


if __name__ == '__main__':
    unittest.main()

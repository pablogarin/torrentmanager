import unittest
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import mock_open
from unittest.mock import patch

from torrentmanager.config import Config


mock_folder = "/test/mock/folder"
mock_quality = "720p"
mock_enforce = "no"
mock_age = "1"
test_config = "[generals]\n" \
    "download_folder = %s\n" \
    "quality = %s\n" \
    "enforce_quality = %s\n" \
    "max_torrent_age = %s\n" % (
        mock_folder,
        mock_quality,
        mock_enforce,
        mock_age)


def input_side_effect(prompt: str):
    if prompt == "Enter a folder to download your shows: ":
        return mock_folder
    elif prompt == "Enter the quality (none, 720p, 1080p or 2160p): ":
        return mock_quality
    elif prompt == "Check quality before download? [y/n] (Default: 'n')":
        return ""
    return prompt


mock_input = Mock(side_effect=input_side_effect)


@patch("builtins.open", new_callable=mock_open, read_data=test_config)
class TestConfig(unittest.TestCase):
    def test_get_config(self, mock_file):
        config = Config()
        self.assertEqual(
            config.get_config("download_folder"),
            mock_folder)
        self.assertEqual(
            config.get_config("quality"),
            mock_quality)
        self.assertEqual(
            config.get_config("enforce_quality"),
            mock_enforce)
        self.assertEqual(
            config.get_config("max_torrent_age"),
            mock_age)

    @patch('builtins.input', mock_input)
    @patch('os.path.exists', return_value=True)
    def test_initial_configuration(self, *args):
        local_mock_open = args[1]
        config = Config()
        config.initial_configuration()
        calls = [
            call("Enter a folder to download your shows: "),
            call("Enter the quality (none, 720p, 1080p or 2160p): "),
            call("Check quality before download? [y/n] (Default: 'n')"),
        ]
        mock_input.assert_has_calls(calls)
        self.assertEqual(mock_input.call_count, 3)
        # Open should be called twice: opening the file and writing to it
        self.assertEqual(local_mock_open.call_count, 2)
        local_mock_open.assert_called_with(config._config_file, "w")

from unittest import TestCase, main
from configuration.base_config import BaseConfig


class TestBaseConfig(TestCase):
    def setUp(self):
        self.LOAD_CONFIG_PATH = 'tests/configuration/config_for_load'
        self.SAVE_CONFIG_PATH = 'tests/configuration/config_for_save'
        self.result = [
            '10.0.0.0',
            '10.0.0.1',
            '10.0.0.2'
        ]

    def tearDown(self):
        try:
            with open(self.SAVE_CONFIG_PATH, 'w'):
                pass
        except Exception as e:
            print('Exception has been occurred while clearing file "{}":'.format(self.SAVE_CONFIG_PATH))

    def test_load_with_default_filename(self):
        config = BaseConfig(self.LOAD_CONFIG_PATH)
        config.load()
        loaded = config.data
        self.assertListEqual(self.result, loaded)

    def test_load_with_filename(self):
        config = BaseConfig()
        config.load(self.LOAD_CONFIG_PATH)
        loaded = config.data
        self.assertListEqual(self.result, loaded)

    def test_save(self):
        config = BaseConfig(self.SAVE_CONFIG_PATH)
        config.data = self.result
        config.save()
        loaded_config = BaseConfig(self.SAVE_CONFIG_PATH)
        loaded_config.load()
        loaded = loaded_config.data
        self.assertListEqual(self.result, loaded)


if __name__ == '__main__':
    main()

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

    def test_load(self):
        config = BaseConfig()
        config.load(self.LOAD_CONFIG_PATH)
        loaded = config.data
        self.assertListEqual(self.result, loaded)

    def test_save(self):
        config = BaseConfig()
        config.data = self.result
        config.save(self.SAVE_CONFIG_PATH)
        loaded_config = BaseConfig()
        loaded_config.load(self.SAVE_CONFIG_PATH)
        loaded = loaded_config.data
        self.assertListEqual(self.result, loaded)


if __name__ == '__main__':
    main()

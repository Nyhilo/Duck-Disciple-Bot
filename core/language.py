from os import path
import json

from core.log import log
from config.settings import settings

_langfile_directory = './langs/'
_langfile_extension = '.json'


class Locale():
    # TODO: Put default locale in config
    default_key = 'en-US'
    current_key = None

    default_locale = None
    current_locale = None

    def __init__(self, base_path) -> None:
        self.base_path = base_path

    def initialize(self) -> None:
        '''Initialize the static application locales. This function should only be called once.'''

        # Set default locale
        self.set_default_locale(self.default_key)

        # Set current locale if it exists in the database, set it to the default otherwise
        locale_key = settings.current_locale_key
        if locale_key is None:
            locale_key = self.default_key

        self.set_locale(locale_key)

    def set_locale(self, locale_key: str) -> str:
        return self._set_locale(locale_key, False)

    def set_default_locale(self, locale_key: str) -> str:
        return self._set_locale(locale_key, True)

    def _set_locale(self, locale_key: str, set_default) -> str:
        # Check if locale file exists
        filepath = f'{_langfile_directory}{locale_key}{_langfile_extension}'

        if not path.exists(filepath):
            raise LookupError

        # Load the file into memory
        with open(filepath, 'r') as f:
            if set_default:
                self._set_default_locale(json.load(f))
                self._set_default_key(locale_key)
                log.info(f'Default locale set to {self.default_key}')
            else:
                self._set_current_locale(json.load(f))
                self._set_current_key(locale_key)
                settings.current_locale_key = locale_key
                log.info(f'Current locale set to {locale_key}')

        # And we're golden I guess
        self.current_key = locale_key

    def get_string(self, path, default_lang=False, **formatkwargs):
        """Combine base path with args path to find correct string for key

        :param path:         Dot-delimited json subpath to target string
        :param default_lang: Whether to use the default language file, defaults
                              to False.

        :param formatkwargs: The keyword arguments to pass to the .format() that
                              gets called on the target string. See the target
                              string in the json for information on what kwargs
                              to provide

        :raises KeyError:    If the given path does not exist in the json
        :raises KeyError:    If the given path is not complete, does not
                              terminate on a string

        :return:             The formatted string in the json at the target path
        """

        fullkey = f'{self.base_path}.{path}'
        fullpath = str.split(fullkey, '.')

        # Navigate down the path of the json object
        try:
            node = self.default_locale if default_lang else self.current_locale
            for step in fullpath:
                node = node[step]

            assert(type(node) is str)

        # The path is not valid, but may exist in the default lang file
        except KeyError:
            if not default_lang:
                return self.get_string(path, default_lang=True, **formatkwargs)

            raise KeyError(f'Path does not exist in lang file: {fullkey}')

        # The given key is valid, but leads to a higher level of nesting
        except AssertionError:
            raise KeyError(f'Key does not lead to a string: {fullkey}')

        # If the node is validated as a string, then we can return it
        return node.format(**formatkwargs)

    @classmethod
    def _set_default_key(cls, key: str) -> None:
        cls.default_key = key

    @classmethod
    def _set_current_key(cls, key: str) -> None:
        cls.current_key = key

    @classmethod
    def _set_default_locale(cls, locale: dict) -> None:
        cls.default_locale = locale

    @classmethod
    def _set_current_locale(cls, locale: dict) -> None:
        cls.current_locale = locale

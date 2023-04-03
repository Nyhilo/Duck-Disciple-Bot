from typing import List
from os import path
import json

_langfile_directory = './langs/'
_langfile_extension = '.json'

class Locale():
    # TODO: Put default locale in config
    default_key = 'en-US'
    current_key = None
    
    default_locale = None
    current_locale = None
    
    def __init__(self, base_path) -> None:
        # Only runs on first init
        if self.default_locale is None:
            self.set_locale(self.default_key, True)
            self.current_locale = self.default_locale
        
        self.base_path = base_path

    def set_locale(self, locale_key:str, set_default:bool=False) -> str:
        # Check if locale file exists
        filepath = f'{_langfile_directory}{locale_key}{_langfile_extension}'

        if not path.exists(filepath):
            raise LookupError

        # Load the file into memory
        with open(filepath, 'r') as f:
            if set_default:
                self.default_locale = json.load(f)
            else:
                self.current_locale = json.load(f)
        
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

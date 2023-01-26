from typing import List
from os import path
import json

_langfile_directory = './langs/'
_langfile_extension = '.json'

class Culture():
    # TODO: Put default culture in config
    default_key = 'en-US'
    current_key = None
    
    default_culture = None
    current_culture = None
    
    def __init__(self, base_path) -> None:
        # Only runs on first init
        if self.default_culture is None:
            self.set_culture(self.default_key, True)
            self.current_culture = self.default_culture
        
        self.base_path = base_path

    def set_culture(self, culture_key:str, set_default:bool=False) -> str:
        # Check if culture file exists
        filepath = f'{_langfile_directory}{culture_key}{_langfile_extension}'
        if not path.exists(filepath):
            return "A file with that culture doesn't exist."

        # Load the file into memory
        with open(filepath, 'r') as f:
            if set_default:
                self.default_culture = json.load(f)
            else:
                self.current_culture = json.load(f)
        
        # And we're golden I guess
        self.current_key = culture_key

    def get_string(self, path, default_lang=False):
        '''Combine base path with args path to find correct string for key'''

        fullkey = f'{self.base_path}.{path}'
        fullpath = str.split(fullkey, '.')

        # Navigate down the path of the json object
        try:
            node = self.default_culture if default_lang else self.current_culture
            for step in fullpath:
                node = node[step]

            assert(type(node) is str)
        
        # The path is not valid, but may exist in the default lang file
        except KeyError:
            if not default_lang:
                return self.get_string(path, True)
            
            raise KeyError(f'Path does not exist in lang file: {fullkey}')
        
        # The given key is valid, but leads to a higher level of nesting
        except AssertionError:
            raise KeyError(f'Key does not lead to a string: {fullkey}')

        # If the node is validated as a string, then we can return it
        return node

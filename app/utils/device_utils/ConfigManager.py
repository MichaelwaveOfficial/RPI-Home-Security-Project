import json
import os


class ConfigManager(object):

    def __init__(self, config_file : str, default_config : dict):

        '''
            Initialise an instance of the applications configuration manager.

            Paramaters:
                * config_file (str) : Path to the JSON configuration file containing device settings.
        ''' 
        
        # JSON containing configuration data. 
        self.config_file = config_file 

        self.settings = default_config.copy() if default_config is not None else {}

        # Ensure the settings file exists. 
        if not os.path.exists(self.config_file) and default_config is not None:
            self.save_settings()

    
    def load_settings(self) -> dict:

        try:

            # If provided path exists, leverage that configuration file. 
            if os.path.exists(self.config_file):
                
                # Read configuration file. 
                with open(self.config_file, 'r') as config_file:

                    # Load values.
                    loaded_settings = json.load(config_file)

                    self.settings.update(loaded_settings)

        except Exception as e:
            raise ValueError(f'Config file {self.config_file} is an invalid JSON.\n\n{e}')

        # Otherwise, if not present; load, save and return default values.
        return self.settings
    

    def save_settings(self):

        ''' Save currently applied settings to a JSON file for later access and retrieval. '''

        # Open config file and write new values.
        with open(self.config_file, 'w') as config_file:
            json.dump(self.settings, config_file, indent=4)


    def type_cast_value(self, value : str | bool | int | list):

        ''' Helper function to enforce type checking when updating values. '''

        # Handle non-string values.
        if not isinstance(value, str):
            value = str(value)

        # Handle bool strings.
        elif value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        
        # Handle integer strings.
        elif value.isdigit():
            value = int(value)
        
        # Handle list strings.
        elif ',' in value:
            value = list(map(int, value.split(',')))
            
        # return original value if no conversion rulesets apply. 
        return value


    def update_settings(self, keys, value):

        ''' Update settings with new values set by the user, save to the config file. '''

        # Type-cast value
        casted = self.type_cast_value(value)

        # Traverse to the target dict
        target = self.settings

        for key in keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
        target[keys[-1]] = casted

        # Persist
        self.save_settings()


    def fetch_current_settings(self):

        ''' Helper function to return current settings stored within the JSON file. '''

        return self.settings
        
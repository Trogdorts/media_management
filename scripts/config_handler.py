import logging
import yaml
class ConfigHandler:
    @staticmethod
    def load_config(config_path):
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Error loading configuration file: {e}", exc_info=True)
            raise

    @classmethod
    def create_default_config(cls, config_path='config.yaml'):
        default_config = {
            'download_directories': {
                'complete': {
                    'movies': 'Z:\\downloads\\complete\\movies',
                    'tv_shows': 'Z:\\downloads\\complete\\tv',
                },
                'duplicate': {
                    'movies': 'Z:\\downloads\\duplicate\\movies',
                    'tv_shows': 'Z:\\downloads\\duplicate\\tv',
                },
                'incomplete': {
                    'movies': 'Z:\\downloads\\incomplete',
                    'tv_shows': 'Z:\\downloads\\incomplete',
                },
            },
            'media_libraries': {
                'movies': 'Z:\\media\\movies',
                'tv_shows': {
                    'adult': 'Z:\\media\\tv_shows\\adult',
                    'kids': 'Z:\\media\\tv_shows\\kids',
                },
            },
            'logging': {
                'level': 'DEBUG',
                'file': 'logs/app.log',
            },
            'settings': {
                'movies': {
                    'delete_failed': True,
                    'delete_unpack': True,
                    'days_to_keep_completed_downloads': 30,
                    'days_to_keep_duplicate_downloads': 30,
                    'days_to_keep_incomplete_downloads': 30,
                    'move_to_duplicates': True,
                    'move_to_library': False,
                },
                'tv_shows': {
                    'delete_failed': True,
                    'delete_unpack': False,
                    'days_to_keep_unpack': 2,
                    'days_to_keep_completed_downloads': 30,
                    'days_to_keep_duplicate_downloads': 30,
                    'move_to_duplicates': True,
                    'move_to_library': False,
                },
            }
        }

        with open(config_path, 'w') as file:
            file.write('# This is the default config file\n')
            yaml.dump(default_config, file)
            logging.info(f"Config file created at {config_path}")

class ShowNamesConfigHandler:
    @staticmethod
    def load_show_names_config(config_path):
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Error loading show names configuration file: {e}", exc_info=True)
            raise

    @classmethod
    def create_default_show_names_config(cls, config_path='show_names.yaml'):
        default_show_names_config = {
            'Nightmares & Dreamscapes - From the Stories of Stephen King': [
                'Nightmares & Dreamscapes From The Stories Of Stephen King'],
            'Coastguard - Every Second Counts': ['Coastguard Search and Rescue']
        }

        with open(config_path, 'w') as file:
            file.write('# This is the default show names config file\n')
            yaml.dump(default_show_names_config, file)
            logging.info(f"Show names config file created at {config_path}")

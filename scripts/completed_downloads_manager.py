import logging
import os
import re
import shutil
from datetime import datetime, timedelta
import copy
import fnmatch
from config_handler import ConfigHandler, ShowNamesConfigHandler
from logging_handler import LoggingHandler
from directory_operations import DirectoryOperations

class MovieProcessor:
    def __init__(self, config):
        self.config = config
        self.completed_movies_downloads_path = config['download_directories']['complete']['movies']
        self.duplicate_movies_downloads_path = config['download_directories']['duplicate']['movies']
        self.incomplete_movie_downloads_path = config['download_directories']['incomplete']['movies']
        self.days_to_keep_completed_movie_downloads = config['settings']['movies']['days_to_keep_completed_downloads']
        self.days_to_keep_duplicate_movie_downloads = config['settings']['movies']['days_to_keep_duplicate_downloads']
        self.days_to_keep_incomplete_movie_downloads = config['settings']['movies']['days_to_keep_incomplete_downloads']
        self.move_to_duplicates_movies = config['settings']['movies']['move_to_duplicates']
        self.move_to_library_movies = config['settings']['movies']['move_to_library']
        self.movie_library = config['media_libraries']['movies']
        self.delete_unpack_movies = config['settings']['movies']['delete_unpack']
        self.delete_failed_movies = config['settings']['movies']['delete_failed']

    def clean_movie_directory_name(self, original_directory_path):
        """Clean and format the folder name to 'movie_name (year)' format."""
        logging.debug(f"Cleaning directory name: {original_directory_path}")

        original_directory_name = os.path.basename(original_directory_path)
        regex = re.compile(r"^(?P<title>.*?)(?:\s|\.|\()?(?P<year>[12][0-9]{3})(?:\D.*)?$")
        re_match = regex.match(original_directory_name)

        if re_match:
            title = re_match.group('title').strip().replace(".", " ").replace(")", "").replace("(", "")
            year = re_match.group('year')
            cleaned_directory_name = f"{title} ({year})"
            logging.debug(f"Cleaned directory name: {cleaned_directory_name}")

            if cleaned_directory_name.lower() == original_directory_name.lower():
                logging.debug(f"Cleaned directory name: {cleaned_directory_name} is the same as: {original_directory_name}")
            return cleaned_directory_name

        else:
            logging.error(f"Year not found in folder name: {original_directory_path}. Skipping rename.")
            return None

    def process_downloaded_movies(self):
        """Process all movie folders."""
        logging.info(f"Starting processing completed movies downloads directory")
        directory_paths = DirectoryOperations.get_directories(self.completed_movies_downloads_path)
        for directory_path in directory_paths:
            cleaned_name = self.clean_movie_directory_name(directory_path)

            new_directory_path = None
            if self.move_to_library_movies:
                temp_directory_path = os.path.join(self.movie_library, cleaned_name)
                if not os.path.isdir(temp_directory_path):
                    new_directory_path = temp_directory_path
                    logging.info(f"Moving '{cleaned_name}' to '{temp_directory_path}'")
                    DirectoryOperations.rename_directory(directory_path, new_directory_path)
                else:
                    logging.info(f"'{cleaned_name}' already exists in '{self.movie_library}'")
            if self.move_to_duplicates_movies and new_directory_path is None:
                temp_directory_path = os.path.join(self.duplicate_movies_downloads_path, cleaned_name)
                count = 1
                while os.path.exists(temp_directory_path):
                    temp_directory_path = os.path.join(self.duplicate_movies_downloads_path, f"{cleaned_name} ({count})")
                    count += 1
                new_directory_path = temp_directory_path
                logging.info(f"Moving '{cleaned_name}' to '{new_directory_path}'")
                DirectoryOperations.rename_directory(directory_path, new_directory_path)
            if not self.move_to_library_movies and not self.move_to_duplicates_movies and new_directory_path is None:
                temp_directory_path = os.path.join(self.completed_movies_downloads_path, cleaned_name)
                count = 1
                while os.path.exists(temp_directory_path):
                    temp_directory_path = os.path.join(self.completed_movies_downloads_path, f"{cleaned_name} ({count})")
                    count += 1
                new_directory_path = temp_directory_path
                logging.info(f"Renaming '{directory_path}' to '{new_directory_path}'")
                DirectoryOperations.rename_directory(directory_path, new_directory_path)
        logging.info(f"Completed processing completed downloads directory.")


class TVShowProcessor:
    def __init__(self, config):
        self.config = config
        self.move_to_duplicates_tv = config['settings']['tv_shows']['move_to_duplicates']
        self.move_to_library_tv = config['settings']['tv_shows']['move_to_library']
        self.completed_tv_shows_downloads_path = config['download_directories']['complete']['tv_shows']
        self.duplicate_tv_shows_downloads_path = config['download_directories']['duplicate']['tv_shows']
        self.kids_tv_shows_library = config['media_libraries']['tv_shows']['kids']
        self.adult_tv_shows_library = config['media_libraries']['tv_shows']['adult']
        self.delete_unpack_tv = config['settings']['tv_shows']['delete_unpack']
        self.delete_failed_tv = config['settings']['tv_shows']['delete_failed']
        self.days_to_keep_unpack_tv = config['settings']['tv_shows']['days_to_keep_unpack']

    def clean_tv_show_directory_name(self, original_directory_path):
        """Clean and format the folder name to 'tv show name S00E00' format."""
        logging.debug(f"Cleaning directory name: {original_directory_path}")
        original_directory_name = os.path.basename(original_directory_path)

        regex = re.compile(r'^(.*?)(S\d{2})(E\d{2}).*$', re.IGNORECASE)

        re_match = regex.match(original_directory_name)

        # Dictionary containing regex patterns and their corresponding replace characters
        show_name_replace_patterns = {
            r'(?<=\w)\.(?=\w)': ' ',  # Replace periods between words with spaces
            r'\.-\.': '',  # Replace .-. with nothing
            r'^\s+': '',  # Replace leading spaces with nothing
            r'\.\s*$': '',  # Replace a trailing period and possible trailing spaces with nothing
            r'\s*\[.*?\]\s*': '',  # Replace anything inside square brackets with nothing
            r'The 1 Percent Club': 'The 1% Club',  # Fix the 1% club shows
            r'John Mulaney Presents Everybodys in L A': 'John Mulaney Presents - Everybody’s in L.A',  # Fix the Everybody’s in L.A show
            r'C S I $': 'CSI - ',  # Fix CSI shows
            r' AU$': ' (AU)',  # Replace trailing ' AU' with ' (AU)'
            r' US$': ' (US)'  # Replace trailing ' US' with ' (US)'
        }

        if re_match:
            show_name = re_match.group(1).strip()
            original_show_name = copy.deepcopy(show_name)
            season = re_match.group(2)
            episode = re_match.group(3)

            # Apply each replace pattern to the show name
            for regex, replace_char in show_name_replace_patterns.items():
                show_name = re.sub(regex, replace_char, show_name)
            cleaned_episode_name = f'{show_name} {season}{episode}'

            if original_directory_path == os.path.join(os.path.dirname(original_directory_path), cleaned_episode_name):
                logging.info(f"Original directory name: {original_directory_path} is the same as: {cleaned_episode_name}")
                return None

            return cleaned_episode_name

        else:
            logging.warning(f"No show name found in '{original_directory_path}'. Skipping rename.")
            return None

    def rename_tv_show_files(self, original_directory_path, new_episode_name):
        """Rename all files within the directory to the new episode name, preserving their extensions."""
        log_entries = []

        try:
            # Iterate through all files in the directory
            for filename in os.listdir(original_directory_path):
                # Skip the .renamed file
                if filename == '.renamed':
                    continue
                old_file_path = os.path.join(original_directory_path, filename)
                if os.path.isfile(old_file_path):
                    file_extension = os.path.splitext(filename)[1]
                    new_file_name = new_episode_name + file_extension
                    new_file_path = os.path.join(original_directory_path, new_file_name)
                    DirectoryOperations.rename_file(old_file_path, new_file_path)

                    # Collect log entries
                    log_entries.append(f"original name: {os.path.basename(old_file_path)}")
                    log_entries.append(f"new name: {new_file_name}")

            # Write log entries to the .renamed file at the end
            if log_entries:
                renamed_file_path = os.path.join(original_directory_path, '.renamed')
                with open(renamed_file_path, 'a') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"Timestamp: {timestamp}\n")
                    for entry in log_entries:
                        f.write(entry + '\n')
                    f.write('\n')  # Add an extra newline for separation between different renaming operations
        except Exception as e:
            logging.error(f"Error while renaming files: {e}")

    def process_downloaded_tv_shows(self):
        """Process all tv show folders."""
        logging.info(f"Starting processing completed tv show downloads directory")

        if self.move_to_library_tv:
            logging.info(f"Getting all existing tv show folders")
            adult_shows = os.listdir(self.adult_tv_shows_library)
            kids_shows = os.listdir(self.kids_tv_shows_library)

        directory_paths = DirectoryOperations.get_directories(self.completed_tv_shows_downloads_path)
        for directory_path in directory_paths:

            if "_FAILED_" in directory_path:
                if self.delete_failed_tv:
                    try:
                        shutil.rmtree(directory_path)
                        logging.info(f"Deleted _FAILED_ tv show download: {directory_path}")
                    except Exception as e:
                        logging.error(f"Unable to delete _FAILED_ tv show download: {e}", exc_info=True)
                else:
                    logging.info(f"Skipping _FAILED_ tv show download: {directory_path}")
                continue

            if "_UNPACK_" in directory_path:
                if self.delete_unpack_tv:
                    cutoff_date = datetime.now() - timedelta(self.days_to_keep_unpack_tv)
                    item_mod_time = datetime.fromtimestamp(os.path.getmtime(directory_path))
                    if item_mod_time < cutoff_date:
                        try:
                            shutil.rmtree(directory_path)
                            logging.info(f"Deleted _UNPACK_ tv show download: {directory_path}")
                        except Exception as e:
                            logging.error(f"Unable to delete _UNPACK_ tv show download: {e}")
                else:
                    logging.info(f"Skipping _UNPACK_ tv show download: {directory_path}")
                continue

            # Skip renaming folders that have already been renamed
            if not os.path.isfile(os.path.join(directory_path, '.renamed')):

                cleaned_name = self.clean_tv_show_directory_name(directory_path)

                if cleaned_name:
                    new_directory_path = None
                    temp_directory_path = os.path.join(self.completed_tv_shows_downloads_path, cleaned_name)

                    if not os.path.exists(temp_directory_path):
                        new_directory_path = temp_directory_path
                        logging.info(f"Moving '{directory_path}' to '{temp_directory_path}'")
                        DirectoryOperations.rename_directory(directory_path, new_directory_path)
                        logging.info(f"Renaming TV Show files in {new_directory_path}")
                        self.rename_tv_show_files(new_directory_path, cleaned_name)

                    elif self.move_to_duplicates_tv:
                        temp_directory_path = os.path.join(self.duplicate_tv_shows_downloads_path, cleaned_name)
                        count = 1
                        while os.path.exists(temp_directory_path):
                            temp_directory_path = os.path.join(self.duplicate_tv_shows_downloads_path, f"{cleaned_name} ({count})")
                            count += 1
                        new_directory_path = temp_directory_path
                        logging.info(f"Moving '{directory_path}' to '{new_directory_path}'")
                        DirectoryOperations.rename_directory(directory_path, new_directory_path)

                    if not self.move_to_library_tv and not self.move_to_duplicates_tv and new_directory_path is None:
                        temp_directory_path = os.path.join(self.completed_tv_shows_downloads_path, cleaned_name)
                        count = 1
                        while os.path.exists(temp_directory_path):
                            temp_directory_path = os.path.join(self.completed_tv_shows_downloads_path, f"{cleaned_name} ({count})")
                            count += 1
                        new_directory_path = temp_directory_path
                        logging.info(f"Renaming '{directory_path}' to '{new_directory_path}'")
                        DirectoryOperations.rename_directory(directory_path, new_directory_path)

        # Process renamed folders to see if they need to be moved to the library
        if self.move_to_library_tv:
            regex = re.compile(r'^(.*?)(S\d{2})(E\d{2}).*$', re.IGNORECASE)
            directory_paths = []
            temp_paths = DirectoryOperations.get_directories(self.completed_tv_shows_downloads_path)
            for directory_path in temp_paths:
                if "_FAILED_" not in directory_path and "_UNPACK_" not in directory_path:
                    directory_paths.append(directory_path)
            for directory_path in directory_paths:
                folder_name = os.path.basename(directory_path)
                re_match = regex.match(folder_name)
                if re_match:
                    show_name = re_match.group(1).strip()
                    season_number = re_match.group(2).lstrip('S').lstrip('0')
                    episode_number = re_match.group(3)

                    base_library_path = None
                    if show_name in kids_shows:
                        base_library_path = self.kids_tv_shows_library
                    elif show_name in adult_shows:
                        base_library_path = self.adult_tv_shows_library
                    if base_library_path:
                        show_path = os.path.join(base_library_path, show_name)
                        season_path = os.path.join(show_path, f'Season {season_number}')
                        if os.path.exists(season_path):
                            existing_episodes = []
                            for episode in os.listdir(season_path):
                                re_match = regex.match(episode)
                                if re_match:
                                    existing_episode_number = re_match.group(3)
                                    existing_episodes.append(str(existing_episode_number))
                            if episode_number not in existing_episodes:
                                logging.info(f"Moving episode '{folder_name}' to '{season_path}'")
                                shutil.move(directory_path, season_path)
                            else:
                                logging.info(f"Episode '{folder_name}' already exists in '{season_path}', moving to duplicates")
                                self.move_to_duplicates(directory_path, cleaned_name)
                        else:
                            logging.info(f"Season path '{season_path}' does not exist, creating it and moving episode")
                            os.makedirs(season_path)
                            shutil.move(directory_path, season_path)

    def move_to_duplicates(self, directory_path, cleaned_name):
        """Move the given directory to the duplicates folder."""
        temp_directory_path = os.path.join(self.duplicate_tv_shows_downloads_path, cleaned_name)
        count = 1
        while os.path.exists(temp_directory_path):
            temp_directory_path = os.path.join(self.duplicate_tv_shows_downloads_path, f"{cleaned_name} ({count})")
            count += 1
        logging.info(f"Moving '{directory_path}' to '{temp_directory_path}'")
        DirectoryOperations.rename_directory(directory_path, temp_directory_path)

        logging.info(f"Completed processing completed downloads directory.")


if __name__ == "__main__":
    config_path = 'config.yml'
    show_names_config_path = 'show_names.yaml'

    if not os.path.exists(config_path):
        ConfigHandler.create_default_config(config_path)

    if not os.path.exists(show_names_config_path):
        ShowNamesConfigHandler.create_default_show_names_config(show_names_config_path)

    try:
        config = ConfigHandler.load_config(config_path)
        show_name_alternates = ShowNamesConfigHandler.load_show_names_config(show_names_config_path)
        LoggingHandler.setup_logging(config)
        movie_processor = MovieProcessor(config)
        tv_show_processor = TVShowProcessor(config)
        movie_processor.process_downloaded_movies()
        tv_show_processor.process_downloaded_tv_shows()
        DirectoryOperations.delete(config['download_directories']['complete']['movies'], config['settings']['movies']['days_to_keep_completed_downloads'])
        DirectoryOperations.delete(config['download_directories']['duplicate']['movies'], config['settings']['movies']['days_to_keep_duplicate_downloads'])
        DirectoryOperations.delete(config['download_directories']['incomplete']['movies'], config['settings']['movies']['days_to_keep_incomplete_downloads'])
        DirectoryOperations.delete(config['download_directories']['complete']['tv_shows'], config['settings']['tv_shows']['days_to_keep_completed_downloads'])
        DirectoryOperations.delete(config['download_directories']['duplicate']['tv_shows'], config['settings']['tv_shows']['days_to_keep_duplicate_downloads'])
        DirectoryOperations.delete(config['download_directories']['incomplete']['tv_shows'], config['settings']['tv_shows']['days_to_keep_incomplete_downloads'])
    except Exception as e:
        logging.critical(f"Critical error in main execution: {e}", exc_info=True)

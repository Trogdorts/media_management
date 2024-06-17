import logging
import os
import shutil
from datetime import datetime, timedelta

class DirectoryOperations:
    @staticmethod
    def get_directories(path):
        """Gather all folders in the given path."""
        return [os.path.join(path, item) for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))]

    @staticmethod
    def rename_directory(original_directory_path, cleaned_directory_name):
        """Rename the directory to the cleaned name."""
        new_directory_path = os.path.join(os.path.dirname(original_directory_path), cleaned_directory_name)
        log_entries = []

        if not original_directory_path == cleaned_directory_name:
            try:
                os.rename(original_directory_path, new_directory_path)
                logging.info(f"Renamed '{original_directory_path}' to '{new_directory_path}'")

                # Collect log entries
                log_entries.append(f"original name: {os.path.basename(original_directory_path)}")
                log_entries.append(f"new name: {cleaned_directory_name}")

                # Write log entries to the .renamed file at the end
                if log_entries:
                    renamed_file_path = os.path.join(new_directory_path, '.renamed')
                    try:
                        with open(renamed_file_path, 'a') as f:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            f.write(f"Timestamp: {timestamp}\n")
                            for entry in log_entries:
                                f.write(entry + '\n')
                            f.write('\n')  # Add an extra newline for separation between different renaming operations
                    except Exception as e:
                        logging.warning(f"Unable to create .renamed file in {new_directory_path}: {e}", exc_info=True)

            except Exception as e:
                logging.error(f"Failed to rename '{original_directory_path}' to '{cleaned_directory_name}': {e}")
        else:
            logging.info(f"Original directory name: {original_directory_path} is the same as: {cleaned_directory_name}")

    @staticmethod
    def rename_file(old_file_path, new_file_path):
        try:
            if not old_file_path == new_file_path:
                os.rename(old_file_path, new_file_path)
                logging.info(f"Renamed '{old_file_path}' to '{new_file_path}'")
            else:
                logging.info(f"File '{old_file_path}' already renamed to '{new_file_path}'")
        except Exception as e:
            logging.warning(f"Failed to rename {old_file_path} to {new_file_path}: {e}", exc_info=True)

    @staticmethod
    def delete(directory, days_to_keep):
        logging.info(f"Checking {directory} for directories older than {days_to_keep} days.")
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                item_mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                if item_mod_time < cutoff_date:
                    try:
                        shutil.rmtree(item_path)
                        logging.info(f"Deleted: {item}")
                    except Exception as e:
                        logging.error(f"Failed to delete '{item_path} with error {e}", exc_info=True)

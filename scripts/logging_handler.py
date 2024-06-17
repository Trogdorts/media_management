import os
import logging



class LoggingHandler:
    @staticmethod
    def setup_logging(config):
        log_level = config.get('logging', {}).get('level', 'DEBUG')
        log_file = config.get('logging', {}).get('file', 'rename_completed_downloads.log')
        try:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', os.path.dirname(log_file))
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_file_path = os.path.join(log_dir, os.path.basename(log_file))
            logging.basicConfig(level=getattr(logging, log_level.upper(), 'INFO'),
                                format='%(asctime)s - %(levelname)s - [Line:%(lineno)s] - %(message)s',
                                handlers=[logging.FileHandler(log_file_path, encoding='utf-8'),
                                          logging.StreamHandler()])
        except Exception as e:
            raise RuntimeError(f"Error setting up logging: {e}")
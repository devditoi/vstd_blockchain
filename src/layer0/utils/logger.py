from rich.console import Console
import os

class Logger:
    def __init__(self, address: str, log_dir: str = "logs"):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file_path = os.path.join(log_dir, f"{address.replace(':', '_')}.log")
        self.log_file = open(log_file_path, "a")
        self.console = Console(file=self.log_file, record=True)

    def log(self, message, style=None):
        self.console.print(message, style=style)

    def __del__(self):
        self.log_file.close()

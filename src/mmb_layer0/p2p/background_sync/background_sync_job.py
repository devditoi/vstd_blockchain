import threading

class BackgroundSyncJob:

    def __init__(self, event_handler):
        self.event_handler = event_handler

    def run(self):
        thread = threading.Thread(target=self.__run)
        thread.start()

    def __run(self):
        self.setup()
        while True:
            self.execution()

    def setup(self):
        pass

    def execution(self):
        pass
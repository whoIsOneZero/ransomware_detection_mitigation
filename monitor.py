import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, on_new_file):
        super().__init__()
        self.on_new_file = on_new_file

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.on_new_file(event.src_path)


def monitor_directory(directory, on_new_file):
    event_handler = FileMonitorHandler(on_new_file)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

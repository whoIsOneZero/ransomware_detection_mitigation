import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, tool):
        self.tool = tool

    def on_created(self, event):
        # Check if the event is a file creation
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.tool(event.src_path)


def start_monitoring(directory, tool):
    event_handler = FileMonitorHandler(tool)
    observer = Observer()
    observer.schedule(event_handler, path=directory, recursive=False)
    observer.start()
    print(f"Monitoring directory: {directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

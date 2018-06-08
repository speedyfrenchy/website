import sass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

last_compile_time = time.time()


def compile_sass():
    global last_compile_time
    """" Watchdog seems to trigger multiple times for every change, 
         so ignore any for a second after the first to stop spamming it """
    if time.time() - last_compile_time > 1:
        print("Recompiling Sass to CSS")
        sass.compile(dirname=('blog/static/sass', 'blog/static/css'), output_style='compressed')
        last_compile_time = time.time()


class SassHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        compile_sass()


handler = SassHandler()
observer = Observer()
observer.schedule(handler, 'blog/static/sass', recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
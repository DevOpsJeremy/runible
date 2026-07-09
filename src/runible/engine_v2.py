
SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


class RunConfig:
    """
    Builds a run configuration instance
    """

    SCHEMA_FILE = SCHEMA_DIR / "run.schema.json"
    with open(SCHEMA_FILE, "r") as f:
        SCHEMA = json.load(f)

    def __init__(self, file):
        self.file = file
        self.config = self.load_config()
        self.clean_config(self.config)
        self.validate_config(self.config)
        self.run = self.get_run()

    def load_config(self):
        return yaml.safe_load(self.file)

    @classmethod
    def validate_config(cls, config):
        try:
            jsonschema.validate(instance=config, schema=cls.SCHEMA)
            return True
        except jsonschema.exceptions.ValidationError as e:
            path = e.json_path.removeprefix("$.")
            msg = f"{e.message} (at {path})" if path else e.message
            raise click.UsageError(msg) from e

    @classmethod
    def clean_config(cls, config):
        return_config = config.copy()

        for step_name, step in config.get("steps", {}).items():
            # Convert strings to list
            for key in ["when", "after"]:
                try:
                    return_config["steps"][step_name][key] = as_list(step[key])
                except KeyError:
                    pass



# old
import networkx as nx
from enum import Enum, auto
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event

# TODO: Delete
class Node:
    pass

class State(Enum):
    PENDING = auto()
    RUNNING = auto()
    SKIPPED = auto()
    FAILED = auto()
    SUCCESS = auto()
    UNKNOWN = auto()

class Run(nx.DiGraph):
    def __init__(self):
        pass

class Engine:
    def __init__(self, run: Run):
        self.run = run

    def handler(self):
        print("in handler")
        starters = [n for n in run.nodes if run.in_degree(n) == 0]
        for starter in starters:
            starter.run()

    def run_thread(self):


    def get_handler_thread(self, daemon: bool = False):
        return Thread(target=self.handler, daemon=daemon)

    def start_handler(self):
        thread = self.get_handler_thread()
        thread.start()

    def handler(self):
        print("in handler")
        for node in self.get_starters():
            print(f"processing node '{node}'")
            self.start_node(node)

        while True:
            event = self.queue.get()
            print(f"Working on {event}")
            self.queue.task_done()

import concurrent.futures
import urllib.request

URLS = ['http://www.foxnews.com/',
        'http://www.cnn.com/',
        'http://europe.wsj.com/',
        'http://www.bbc.co.uk/',
        'http://nonexistent-subdomain.python.org/']

# Retrieve a single page and report the URL and contents
def load_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()

# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('%r page is %d bytes' % (url, len(data)))
from datetime import datetime
import networkx as nx
from enum import Enum, auto
from threading import Thread, Event

from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

URLS = ['http://www.foxnews.com/',
        'http://www.cnn.com/',
        'http://europe.wsj.com/',
        'http://www.bbc.co.uk/',
        'http://nonexistent-subdomain.python.org/']

def print_output(text):
    print(f"{datetime.now()}: {text}")

with ThreadPoolExecutor(max_workers=5) as executor:
    output_result = {executor.submit(print_output, t): t for t in URLS}
    for thing in as_completed(output_result):
        print(f"Thing: {thing}")

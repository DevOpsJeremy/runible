from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from .plan import Graph

# TODO: Delete
from datetime import datetime
import time
import random


class Run:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.threads = []

    @classmethod
    def from_file(cls, file):
        graph = Graph.from_file(file)
        return cls(graph)

    def run(
        self,
        fn,
        max_workers: int = 5,
        thread_pool_initializer=None,
        thread_pool_initargs=None,
        *args,
        **kwargs,
    ):
        remaining = {node: self.graph.in_degree(node) for node in self.graph.nodes}

        future_to_step = {}

        with ThreadPoolExecutor(
            max_workers=max_workers,
            initializer=thread_pool_initializer,
            initargs=thread_pool_initargs,
        ) as executor:
            for node_name in self.graph.nodes:
                if self.graph.in_degree(node_name) == 0:
                    node = self.graph.nodes[node_name]
                    f = executor.submit(fn, *args, **kwargs, **node)
                    future_to_step[f] = node_name

            while future_to_step:
                f = next(as_completed(future_to_step))
                node_name = future_to_step.pop(f)

                for successor_name in self.graph.successors(node_name):
                    remaining[successor_name] -= 1

                    if remaining[successor_name] == 0:
                        successor = self.graph.nodes[successor_name]
                        f = executor.submit(fn, *args, **kwargs, **successor)
                        future_to_step[f] = successor_name


# TODO: Delete
def run_step(step):
    wait_time = random.randint(1, 2)

    print(f"{datetime.now()} : START({step.name})")
    time.sleep(wait_time)
    print(f"{datetime.now()} : END({step.name})")

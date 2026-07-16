import io
import time
import threading

import pytest
import click

from runible import engine


def test_stepconfig_defaults_and_str():
    s = engine.StepConfig(name="s1", run="echo", vars=None, after=None, when=None)
    assert s.name == "s1"
    assert s.run == "echo"
    assert s.vars == {}
    assert s.after == []
    assert s.when == []
    assert "s1" in str(s)


def test_runconfig_get_steps_merges_vars():
    rc = engine.RunConfig(
        vars={"gv": 1}, steps={"step1": {"run": "echo hi", "vars": {"lv": 2}}}
    )

    steps = list(rc.steps)
    assert len(steps) == 1
    step = steps[0]
    # global vars merged with local
    assert step.vars["gv"] == 1
    assert step.vars["lv"] == 2


def test_clean_content_converts_strings_to_lists():
    content = {"steps": {"s": {"run": "r", "after": "a", "when": "w"}}}
    engine.RunConfig.clean_content(content)
    assert isinstance(content["steps"]["s"]["after"], list)
    assert content["steps"]["s"]["after"] == ["a"]
    assert isinstance(content["steps"]["s"]["when"], list)
    assert content["steps"]["s"]["when"] == ["w"]


def test_validate_content_raises_on_missing_required():
    content = {"steps": {"s1": {}}}  # missing 'run'
    with pytest.raises(click.UsageError):
        engine.RunConfig.validate_content(content)


def test_graph_build_unknown_dependency_raises_attribute_error():
    yaml = """
    steps:
      a:
        run: echo a
      b:
        run: echo b
        after: missing
    """
    f = io.StringIO(yaml)
    graph = engine.Graph(engine.RunConfig.load_content(f))
    # build should raise because 'missing' dependency does not exist; current implementation
    # leads to an AttributeError when trying to access dep.name on None
    with pytest.raises(AttributeError):
        graph.build()


def test_graph_cycle_detection_raises_valueerror():
    yaml = """
    steps:
      a:
        run: echo a
        after: b
      b:
        run: echo b
        after: a
    """
    f = io.StringIO(yaml)
    with pytest.raises(ValueError):
        engine.Graph.from_file(f)


def test_run_respects_dependencies_and_submits_successors_only_after_completion():
    yaml = """
    steps:
      a:
        run: echo a
      b:
        run: echo b
        after: a
      c:
        run: echo c
        after: a
    """
    f = io.StringIO(yaml)
    run = engine.Run.from_file(f)

    records = []
    lock = threading.Lock()

    def fn(step):
        # record start
        with lock:
            records.append(("start", step.name, time.time()))
        # small work
        time.sleep(0.02)
        with lock:
            records.append(("end", step.name, time.time()))
        return step.name

    run.run(fn, max_workers=3)

    # collect times
    starts = {}
    ends = {}
    for typ, name, t in records:
        if typ == "start":
            starts.setdefault(name, []).append(t)
        else:
            ends.setdefault(name, []).append(t)

    # ensure a started and ended
    assert "a" in starts and "a" in ends
    # ensure b and c started after a ended (they should only be submitted after a completes)
    a_end = min(ends["a"]) if ends["a"] else None
    b_start = min(starts["b"]) if "b" in starts else None
    c_start = min(starts["c"]) if "c" in starts else None

    assert a_end is not None
    assert b_start is not None and b_start >= a_end - 1e-6
    assert c_start is not None and c_start >= a_end - 1e-6

import io
from runible import engine


def test_workflow_run_order(capsys):
    yaml = """
    steps:
      a:
        run: echo a
        after: c
      b:
        run: echo b
        after: a
      c:
        run: echo c
    """
    f = io.StringIO(yaml)
    workflow = engine.Workflow(engine.Graph.from_file(f))

    def fn(step, *args, **kwargs):
        print(step.name)

    workflow.run(fn)
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.splitlines() == ["c", "a", "b"]

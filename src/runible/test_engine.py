from runible import engine


def test_workflow_run_order(tmp_path, capsys):
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
    plan_path = tmp_path / "tmp_plan.yml"
    plan_path.write_text(yaml)
    with open(plan_path, "r") as f:
        workflow = engine.Workflow(engine.Graph.from_file(f))

    def fn(step, *args, **kwargs):
        print(step.name)

    workflow.run(fn)
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.splitlines() == ["c", "a", "b"]

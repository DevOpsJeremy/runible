import io
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

def test_search_paths(tmp_path, capsys):
    playbook_name_valid = "playbook1.yml"
    playbook_path = tmp_path / playbook_name_valid
    plan_path_valid = tmp_path / "plan.yml"

    playbook_content = """
    - hosts: localhost
      tasks:
        - ping:
    """
    plan_content_valid = f"""
    steps:
      step1:
        run: {playbook_name_valid}
    """

    playbook_path.write_text(playbook_content)
    plan_path_valid.write_text(plan_content_valid)
    with open(plan_path_valid, "r") as f:
        engine.Workflow(engine.Graph.from_file(f)).run(fn=engine.Step.invoke)

    playbook_name_invalid = "missing_playbook.yml"
    plan_path_invalid = tmp_path / "invalid_plan.yml"
    plan_content_invalid = f"""
    steps:
      step1:
        run: {playbook_name_invalid}
        env:
          ANSIBLE_NOCOLOR: true
    """

    plan_path_invalid.write_text(plan_content_invalid)
    with open(plan_path_invalid, "r") as f:
        engine.Workflow(engine.Graph.from_file(f)).run(fn=engine.Step.invoke)
    captured = capsys.readouterr()
    print(captured.out.splitlines()[0] )
    assert captured.out.splitlines()[0] == f"[ERROR]: the playbook: {playbook_name_invalid} could not be found"

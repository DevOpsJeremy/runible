import ansible_runner

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


def test_tags_and_skip_tags_merge_and_cmdline(tmp_path, monkeypatch):
    yaml = """
    tags: [plan_tag]
    skip_tags: [plan_skip]
    steps:
      step1:
        run: echo test
        tags: [step_tag]
        skip_tags: [step_skip]
    """
    plan_path = tmp_path / "plan.yml"
    plan_path.write_text(yaml)

    with open(plan_path, "r") as f:
        plan = engine.Plan.from_file(f)

    # there should be a single step with merged tags/skip_tags
    assert len(plan.steps) == 1
    step = plan.steps[0]
    assert set(step.tags) == {"plan_tag", "step_tag"}
    assert set(step.skip_tags) == {"plan_skip", "step_skip"}

    captured = {}

    def fake_run(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(ansible_runner.interface, "run", fake_run)

    # invoke the step which should call the patched ansible_runner.interface.run
    step._invoke()

    # cmdline must include both --tags and --skip-tags with merged values
    assert "cmdline" in captured
    assert "--tags plan_tag,step_tag" in captured["cmdline"]
    assert "--skip-tags plan_skip,step_skip" in captured["cmdline"]


def test_no_tags_no_cmdline(tmp_path, monkeypatch):
    yaml = """
    steps:
      s:
        run: echo nothing
    """
    plan_path = tmp_path / "plan2.yml"
    plan_path.write_text(yaml)

    with open(plan_path, "r") as f:
        plan = engine.Plan.from_file(f)

    step = plan.steps[0]

    captured = {}

    def fake_run(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(ansible_runner.interface, "run", fake_run)

    step._invoke()

    # no cmdline should be provided when there are no tags/skip_tags
    assert "cmdline" not in captured or captured.get("cmdline", "") == ""

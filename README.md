# Runible

Ansible workflow orchestrator.

## Installation

Install with pip:

```bash
pip install runible
```

## Usage

A **Run** is configured with a list of **Steps**. Each step runs a playbook, along with optional extra vars or tags.

`configure_infra.yml`

```yaml
vars:
  domain: devopsjeremy.com

steps:
  prepare:
    run: prepare.yml
    tags:
      - bootstrap
  routers:
    run: routers.yml
    after:
      - prepare
    vars:
      ansible_user: rtr_admin
  servers:
    run: servers.yml
    after:
      - prepare
  desktops:
    run: desktops.yml
    after:
      - servers
```

To invoke the run:

```bash
runible run configure_infra.yml
```

This will run the `prepare.yml` playbook, followed by `routers.yml` and `servers.yml`. Once `servers.yml` is completed, the `desktops.yml` playbook runs.

`prepare` ╭─◎ `routers`
◎───────┤
        ╰─◎────────◎ `desktops`
          `servers`

HTML:
<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#9581;<br/>
&#9678;&#9472;&#9472;&#9472;&#9472;&#9508;

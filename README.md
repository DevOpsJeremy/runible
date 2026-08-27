# Runible

Ansible workflow orchestrator.

## Installation

Install using pip:

```bash
pip install runible
```

## Usage

A **Run** is configured with a list of **Steps**. Each step runs an playbook, along with optional extra vars or tags.

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


# Visual workflow interface plugin plan

## Goal

Add a built-in `workflow` interface plugin that presents a live, terminal-native
view of a Runible plan as it executes.  It should feel like a small CI/CD
pipeline: every declared step is visible from the beginning, dependency edges
make the execution order clear, and node appearance changes immediately as
Ansible events arrive.

The implementation should use the already-declared `textual` dependency.  The
first version is deliberately an observability interface: it must not change
workflow scheduling, cancellation, or Ansible invocation behavior.

## Confirmed integration contract

`Plan` creates exactly one interface instance. `Graph` then builds the DAG, and
`Workflow.run()` invokes ready `Step` objects concurrently (up to five worker
threads by default). Each invocation has the following signal path:

| Runible callback | Interface method | When the workflow plugin uses it |
| --- | --- | --- |
| `Step.start()` | `start(sender)` | Initialise the diagram on the first step and mark that step running. |
| `event_handler(event_data)` | `event(sender, **event_data)` | Retain a short status/detail line and infer task-level progress where the event payload provides it. |
| `status_handler(status_data, runner_config)` | `status(sender, status_data, runner_config)` | Update runner status text; use terminal failure/cancel status as early state information. |
| `finished_callback(runner)` | `finished(sender, runner)` | Determine the definitive per-step outcome from the runner result/status. |
| `cancel_callback()` | `cancel(sender)` | Mark the step cancelled. |
| `artifacts_handler(artifact_dir)` | `artifacts(sender, artifact_dir)` | Store/display the artifact location in the selected-step detail. |
| `Step.end()` | `end(sender)` | Finalise a step that returned without a more specific terminal state; close the UI only after all started work is terminal. |

Two details affect the design:

1. `start` and `end` are emitted directly around `ansible_runner.interface.run()`;
   the other methods are adapters for ansible-runner callbacks.
2. Since `Workflow` uses a thread pool, callbacks can be concurrent and never
   should mutate Textual widgets directly.

The complete topology is nevertheless available at the first callback:
`sender.plan.steps` contains every `Step`, each `Step.after` contains its
predecessor names, and plan declaration order is stable. This avoids adding a
new engine hook for the initial plugin.

## User experience and rendering scope

The main panel is a compact DAG rendered from a fixed state model. Columns are
topological levels (`0` for roots; otherwise `1 + max(predecessor level)`) and
rows use the YAML declaration order. This gives a predictable left-to-right
pipeline while preserving parallel branches. A right-hand or lower detail pane
shows the selected step's current state, last Ansible status/event summary,
artifact path, and final result.

Use a one-cell node glyph and box-drawing connectors:

| State | Node treatment |
| --- | --- |
| pending | `◎` (U+25CE), dim/neutral |
| running | rotating `◐`, `◓`, `◑`, `◒` spinner, yellow |
| successful | `●` in green for the first version; permit a future check-mark theme |
| failed | `✕` or `●` in red |
| cancelled | `⊘` in yellow/red |
| unknown/interrupted | `?`, muted |

For every directed dependency, route a connector from the predecessor's right
edge to the successor's left edge. Use `─` for horizontal runs, `│` for vertical
runs, and corner pairs such as `╭`/`╮` and `╰` (U+2570)/`╯` at turns. Reserve
connector lanes between adjacent step rows so edges do not overwrite nodes or
labels. The first pass should support the common cases (linear and branching
DAGs) well; where routing lanes collide, choose an additional outer lane rather
than attempting a crossed or ambiguous connection. Render node labels alongside
their glyphs, truncate to the available terminal width, and include a legend.

The spinner advances from a Textual interval timer (for example, 125 ms), not
from Ansible event frequency. This keeps a quiet long-running playbook visibly
alive.

## Textual application design

Implement the interface as a purpose-built Textual `App`, not a collection of
one widget per node. A widget-per-node approach makes connector painting,
overlap avoidance, and resize behavior unnecessarily difficult. Instead use
three stable regions:

```text
┌ Runible workflow ─────────────────────────────────────────────────────────┐
│  Running: 2   Passed: 1   Failed: 0   Pending: 3     [h] Help  [q] Quit    │
├───────────────────────────────┬────────────────────────────────────────────┤
│                               │ Selected: deploy                            │
│ ◎ validate ──╮                │ State: pending                              │
│              ╰── ◓ build ──╮ │ Depends on: build                           │
│                 ╰── ◐ lint │ Last event: TASK [compile]                    │
│                            ╰── ◎ deploy                                    │
│                               │ Artifacts: /…                               │
├───────────────────────────────┴────────────────────────────────────────────┤
│ ↑/↓ select · Enter focus detail · h help · q quit                           │
└────────────────────────────────────────────────────────────────────────────┘
```

- `Header`/custom status bar: plan summary and contextual key hints.
- `WorkflowDiagram(Widget)`: the only owner of graph drawing. It exposes a
  `render()` method that creates a `rich.text.Text` object line by line, with
  spans for semantic styles. It reads an immutable snapshot of the view model;
  it does not own mutable workflow state.
- `StepDetails(Static)`: shows the selected node's metadata and bounded recent
  events. It must be scrollable for narrow/short terminals.
- `Footer`/custom command bar: current action hints and transient errors.
- `HelpScreen(ModalScreen)`: generated from registered Textual bindings so the
  help view never drifts from the actual available hotkeys.

Use a module-local `WORKFLOW_CSS` string or a colocated
`src/runible/plugins/workflow.tcss` stylesheet. A dedicated `.tcss` file is
preferable once the widget layout exists because it can be reloaded during
Textual development. The initial selectors should establish terminal-safe
structure rather than encode graph colors in CSS:

```tcss
Screen { layout: vertical; background: $surface; }
#summary { height: 1; padding: 0 1; background: $panel; }
#body { height: 1fr; layout: horizontal; }
#diagram { width: 2fr; min-width: 30; padding: 1; overflow: auto; }
#details { width: 1fr; min-width: 28; border-left: tall $primary; padding: 1; overflow-y: auto; }
#command-bar { height: 1; padding: 0 1; background: $panel; }
.warning { color: $warning; }
.error { color: $error; }
```

The diagram's per-state colours belong in Rich styles (`workflow-pending`,
`workflow-running`, `workflow-success`, and so on) applied to node glyph
spans. This lets one connector remain neutral while a node changes state
without rebuilding Textual widget trees. Provide an ASCII fallback glyph theme
for terminals that cannot render box-drawing or ambiguous-width Unicode.

## Deterministic DAG layout and drawing

The layout engine should be a pure function:
`layout(steps_in_declaration_order) -> DiagramLayout`. It needs no Textual or
Ansible dependency and returns node cells, label cells, and ordered connector
segments. This is important because Textual redraws on resize while the graph
itself does not change.

1. Compute a stable topological level for every node: roots use column 0 and a
   node uses one column beyond its deepest predecessor. Preserve YAML
   declaration order as the tie-breaker within a level.
2. Assign a row to every node. Start with declaration order, then reserve blank
   rows between nodes that need a vertical edge route. The row assignment must
   be stable across state changes so a spinner does not cause the diagram to
   jump.
3. Give each level a fixed minimum width based on the longest visible label in
   that level, capped by the viewport. Place a node at the beginning of its
   level and render its label immediately after its glyph. If width is limited,
   preserve glyphs/edges, truncate labels with an ellipsis, and let the diagram
   scroll horizontally; do not recompute the topology into a misleading layout.
4. Route each edge in a deterministic order (source row, target row, then
   declaration order). Draw horizontally from the source label's right edge to
   a free lane, vertically on that lane, and horizontally into the target
   glyph. Select the nearest free lane; reserve its cells so a later edge gets
   an outer lane. Use `╭`/`╮`/`╰`/`╯`, `─`, and `│` at the segment turns. At a
   shared endpoint, draw a junction-compatible connector before drawing the
   node itself so the node glyph always wins.
5. Composite onto a character-cell buffer first, with a parallel style buffer.
   Define precedence as node > label > connector > blank, and define a small
   connector merge table (`─ + │` becomes `┼`, etc.) for legitimate crossings.
   Convert the final rows to `Text` only after all nodes and edges are placed.
   This prevents drawing order from corrupting the graph.
6. On `Resize`, rerender the same `DiagramLayout` for the new viewport. Only
   recalculate column widths/truncation and scroll bounds; retain graph levels,
   rows, lanes, selection, and state.

Initial scope is an orthogonal left-to-right DAG, including linear chains,
fan-out, fan-in, and parallel branches. It is intentionally not a general
graph-drawing engine; an extremely dense graph remains readable through
scrolling and the details pane, with a future collapse/filter feature available
if real plans demand it.

## Actions and hotkey foundation

Define an action layer from the first implementation even though operational
actions are not yet chosen. The app owns Textual `Binding` declarations and
`action_*` methods; diagram widgets send selection/navigation intent to the app
instead of handling global keys themselves. This keeps future commands out of
the callback and rendering paths.

Ship only safe, local actions initially:

| Binding | Textual action | Initial behavior |
| --- | --- | --- |
| `up` / `k`, `down` / `j` | `select_previous` / `select_next` | Move the selected step in visual/declaration order. |
| `left` / `h`, `right` / `l` | `select_dependency` / `select_dependent` | Move through the selected node's DAG relationships. |
| `enter` | `toggle_details` | Focus/collapse the details pane. |
| `r` | `refresh_view` | Repaint from the latest model snapshot. |
| `?` | `show_help` | Open the binding-derived help modal. |
| `q` / `ctrl+c` | `request_quit` | Use the confirmation/finished behavior described above. |

Represent future workflow-affecting controls as an explicit command interface,
for example `WorkflowCommand(name, selected_step, arguments)` and an optional
`command_handler` supplied by a future engine integration. Keep these bindings
disabled or absent until the command has a safe implementation. In particular,
do not let a Textual hotkey mutate `Workflow` internals or call Ansible runner
objects directly from the UI thread. When actions such as cancel, retry,
rerun, or open-artifacts are defined, they should be registered as bindings
with availability predicates based on the selected node state, dispatched to a
thread-safe command queue, and confirmed when destructive.

## Implementation plan

1. Create `src/runible/plugins/workflow.py` with a `WorkflowInterface(Interface)`.
   Its constructor calls `super().__init__(quiet=True)`, creates a lock-protected
   workflow state object, and has no terminal side effects yet. Add the
   `workflow = "runible.plugins.workflow:WorkflowInterface"` entry point in
   `pyproject.toml`, plus a short user-facing documentation/example update.

2. Define a UI-independent model in the module (or a small adjacent private
   module): `StepState` enum, `StepViewModel` (name, dependencies, status,
   runner result, latest event/status summary, artifacts, timestamps), and
   `WorkflowViewModel` (ordered steps, computed levels, selected step, shutdown
   state). Give it explicit, idempotent transition methods so duplicate or
   out-of-order callbacks cannot regress a terminal node to running.

3. Lazily initialise the model in `start(sender)`. Build all view models from
   `sender.plan.steps`, validate every `after` reference defensively, compute
   levels, and precompute connector routes. Then transition `sender.name` to
   running. This initialization must be guarded by a lock because multiple root
   steps may start at the same time.

4. Build the Textual app, `WorkflowDiagram` cell-buffer renderer, details pane,
   custom status/command bars, TCSS stylesheet, and binding/action foundation
   described above. Keep model transitions, layout/routing, glyph selection,
   and UI rendering separable so they can be unit tested without a TTY.

5. Start the Textual app once, in a dedicated UI thread, when the model is first
   initialized. Callback methods acquire/update the model lock, then use
   Textual's thread-safe scheduling mechanism (`call_from_thread` or a posted
   message) to request a refresh. Do not call widgets, timers, or `refresh()`
   directly from worker threads. Arrange a startup-ready event so callbacks that
   arrive immediately do not drop the initial state update.

6. Implement callback semantics:
   - `event`: extract only stable, useful fields (`event`, `event_data.task`,
     `event_data.task_action`, `event_data.host`, `stdout`) into a bounded
     recent-event buffer; never render raw event dictionaries into the diagram.
   - `status`: store a concise runner status and, when it is clearly terminal,
     apply a terminal state without waiting for `finished`.
   - `finished`: map the runner's `status`/`rc` into success, failure, or
     cancelled. Record the result before refreshing.
   - `cancel`: immediately mark cancelled unless a success/failure is already
     definitive.
   - `artifacts`: attach the path to the step details.
   - `end`: if no terminal callback was received, mark the step as
     unknown/interrupted (not successful). It should also re-evaluate whether
     the UI can close.

7. Define shutdown behavior explicitly. Keep the final diagram visible until
   the workflow has no active nodes; then show a final summary and exit on a
   short configurable grace interval or user keypress. A future enhancement can
   add a `--no-wait`/environment setting. If workflow execution aborts before
   dependent steps are scheduled, leave those nodes pending and surface a
   workflow-interrupted banner rather than falsely marking them passed.

8. Add focused tests. Unit-test topology levels, row/lane routing, connector
   merge/precedence rules, truncation, glyph/color selection, and every allowed
   state transition. Test callbacks with synthetic `Step` and runner objects,
   including concurrent `start` calls and a missing `finished` callback. Use
   Textual's test harness for queued refreshes, spinner ticks, every initial
   binding, the help modal, resize behavior, and disabled future-action
   handling. Preserve the existing engine tests and add an entry-point loading
   test for `interface: workflow`.

9. Manually verify against `examples/runible.yml`: check the `step1 → step2` and
   `step1 → step3` fan-out, `step2 → step4` continuation, parallel running
   spinners, a failing playbook, cancellation, narrow terminal width, and a
   non-interactive/redirected stdout invocation. For non-TTY output, detect the
   condition and fall back to a concise final text summary rather than emitting
   escape sequences.

## Acceptance criteria

- `interface: workflow` loads through the existing `runible` entry-point group.
- Before any Ansible output completes, the display shows all steps and their
  dependencies from the plan.
- Running, successful, failed, cancelled, and interrupted states are visually
  distinct, and running nodes animate independently of event volume.
- Parallel steps update correctly without UI-thread exceptions, corrupted
  rendering, or lost terminal states.
- The existing `default` and `log` interfaces behave unchanged.
- The plugin works in a TTY and degrades safely to a final summary when no TTY
  is available.

## Deferred decisions

- Whether success uses a green filled circle (the simplest visual system) or a
  check mark; the state model keeps this purely a theme decision.
- More sophisticated edge crossing minimisation, zoom/pan, filtering, and
  per-task subgraphs. These should wait until the basic DAG view proves useful.
- Engine-level lifecycle signals for plan start/end. They are not required for
  the first implementation, but would make abort/shutdown semantics more exact
  in a later iteration.

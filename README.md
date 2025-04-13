# README.md - TaskCrafter

# 🛠️ TaskCrafter

TaskCrafter is a developer-first, CLI-based task scheduler that lets you define jobs in YAML, chain them with flexible logic, and extend them with Python plugins, shell scripts, or containers. Ideal for automating workflows without bloated CI/CD systems.

---

### 🚀 Why TaskCrafter?

- ✅ Declarative YAML job definitions
- 🔁 Chain jobs with `on_success`, `on_failure`, `depends_on`, etc.
- 🧩 Python plugin architecture, container execution, and binary support
- 📥 Inputs/Outputs between jobs with cache-based file passing
- 🧠 Templating and variable resolution from env, files, or results
- 📦 Git-friendly and lightweight
- 🕹️ CLI-first, built for developers and DevOps
- 🧯 Timeout, retries, cron scheduling, and log file support

---

## 📦 Installation

```bash
git clone https://github.com/your-org/taskcrafter
cd taskcrafter
make build  # optional, for creating a standalone binary
```

---

## 📝 Example jobs.yaml

```yaml
jobs:
  - id: hello
    name: Hello World
    plugin: hello
    params:
      message: "Hello from %JOB_ID%!"
    enabled: true
    timeout: 10
    retries:
      count: 2
      interval: 5

  - id: follow_up
    name: Follow-up
    plugin: hello
    params:
      message: "Output was: {{ inputs.hello.result }}"
    depends_on:
      - hello
    input:
      result: "result:hello"
```

---

## 🧩 Plugin System

```python
class Plugin:
    name = "hello"
    description = "Simple Hello plugin"
    long_description = "A simple plugin to print greetings"

    def run(self, params, inputs=None):
        print(params.get("message", "HELLO WORLD"))
```

- All plugins are auto-registered
- You can define metadata, description, and structured output
- Plugins can access job inputs via `inputs` param

---

## 🕹️ CLI Usage

```bash
taskcrafter list                # List all jobs
taskcrafter run <job_id>        # Run a specific job
taskcrafter run                 # Run the full DAG
taskcrafter preview             # Visualize job flow
```

Global flags:

- `--file <path>`: Use a different YAML job file

---

## 🧪 Development

- Written in Python 3.10+
- Modular architecture
- Plugin-based
- Easy to test and extend

Using make:

```bash
Targets:
  install    Install dependencies
  lint       Run flake8
  test       Run tests with pytest
  coverage   Run tests and show coverage
  build      Build standalone binary with PyInstaller
  all        Run format, lint and test
  clean      Remove temporary files and build artifacts
  docker     Build and run container (use CONTAINER_TOOL to specify podman or docker)
```

---

## ✅ TODO Roadmap

- [x] `depends_on`, `on_finish` etc. should support job params, not just IDs
      I am having 2nd thoughts on this, mainly because we can end in the loop of
      job under the job under the job under the job..

      I'll rethink the idea, if needed.

- [✅] Automatically exit if no jobs are running
- [✅] Add summary table report after run
- [ ] New plugin type: `terminate`
- [ ] Add `before_all`, `after_all`, `on_error`, `on_skip` global hooks
- [ ] Support for job `input` and `output` resolution
- [ ] Docs: Document plugin dev best practices
- [ ] Add `--log-file` and `--log-level` CLI flag
- [ ] More unit tests, get to 100% code coverage 😊

---

## 📄 License

MIT License. Contributions welcome!

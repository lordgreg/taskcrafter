# 🛠️ TaskCrafter

TaskCrafter is a developer-first, CLI-based task scheduler that lets you define jobs in YAML, chain them with flexible logic, and extend them with Python plugins or shell scripts. Ideal for automating developer workflows without relying on heavy CI/CD systems.

---

### 🚀 Why TaskCrafter?

- ✅ Write jobs in YAML (not spaghetti shell scripts)
- 🔁 Chain tasks with conditions: `on_success`, `on_failure`, `depends_on`
- 🧩 Extend with Python plugins, Docker containers, or local binaries
- 🧠 Templating support in parameters
- 📦 Git-friendly (keep jobs versioned alongside code)
- 🪄 CLI-first, DevOps-inspired design
- 🔐 Job timeout, retry logic, and scheduler support
- 📈 Visualize job flow directly in the terminal

---

## 📦 Installation

```bash
git clone https://github.com/your-org/taskcrafter
cd taskcrafter
make build  # optional, to create a standalone binary
```

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
    max_retries:
      count: 2
      interval: 5

  - id: dependent_job
    name: Follow-up
    plugin: hello
    params:
      message: "Executed after hello."
    depends_on:
      - hello
```

---

## 🧩 Plugin System

Each plugin is a Python class with a required `run(params)` method:

```python
class Plugin:
    name = "hello"
    description = "Simple Hello plugin"

    def run(self, params):
        print(params.get("message", "HELLO WORLD"))
```

Plugins are automatically registered via `plugin_registry`.

---

## 🕹️ CLI Usage

```bash
taskcrafter list                 # List all jobs
taskcrafter run <job_id>         # Run a job by ID
taskcrafter validate             # Validate the job file
taskcrafter preview              # Show job flow as a graph
taskcrafter explain <job_id>     # Show details of a specific job
```

Optional flags:

- `--file <path>`: Use a different jobs YAML file
- `--force`: Force job execution even if disabled

---

## 🧠 Advanced Features

- `on_success`, `on_failure`: Automatically trigger chained jobs
- `depends_on`: Ensure jobs only run after dependencies
- `max_retries`: Retry logic with intervals
- `timeout`: Cancel jobs that run too long
- `schedule`: Support for cron-like background jobs
- `container`: Run jobs inside Docker containers
- `binary`: Execute native binaries

---

## 📈 Visual Preview

```bash
taskcrafter preview
```

Displays a tree of job dependencies using `rich` in your terminal.

---

## 🧪 Development

- Written in Python 3.10+
- Modular plugin system
- Well-structured for contribution

```bash
make test       # Run tests
make lint       # Run linter
```

---

## 📄 License

MIT License. Contributions welcome!

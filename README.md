# 🛠️ TaskCrafter

TaskCrafter is a developer-first, CLI-based task scheduler that lets you define jobs in YAML, chain them with flexible logic, and extend them with Python plugins, shell scripts, or containers. Ideal for automating workflows without bloated CI/CD systems.

---

### 🚀 Why TaskCrafter?

- ✅ Declarative YAML job definitions
- 🔁 Chain jobs with `on_success`, `on_failure`, `depends_on`, etc.
- 🪝 Use global hooks `before_all`, `after_all`, `on_error`, `before_job` and `after_job`
- 🧩 Python plugin architecture, container execution, and binary support
- 🐋 Executing jobs using containers (Podman support included!)
- 📥 Inputs/Outputs between jobs with cache-based file passing
- 🧠 Templating and variable resolution from env, files, or results
- 📦 Git-friendly and lightweight
- 🕹️ CLI-first, built for developers and DevOps
- 🧯 Timeout, retries, cron scheduling, and log file support

---

## 📦 Local setup

_If you want to run TaskCrafter locally, follow these steps:_

```bash
# make sure you have .venv and requirements.txt installed
python -m venv .venv
source .venv/bin/activate

# install requirements
make install

# run TaskCrafter
python main.py
```

- For debugging, vscode is suggested, all launcher options can be found in [`.vscode/launch.json`](.vscode/launch.json). Note that you need to install the `debugpy` extension for vscode to work. Feel free to use nvim (with nvim-dap and nvim-dap-python) if you prefer. As a matter of fact, you can use any editor you like. 🐕

---

## 📝 Example jobs.yaml

There are a-lot of examples already provided, please see the [`examples/jobs/`](examples/jobs) folder.

---

## 🧩 Plugin System

```python
class Plugin(PluginInterface):
    name = "hello"
    description = "Simple Hello plugin"
    long_description = "A simple plugin to print greetings"

    def run(self, params):
        print(params.get("message", "HELLO WORLD"))

        return { "message": "I am a plugin", "foo": "bar" }
```

- All plugins are auto-registered
- You can define metadata, description, and structured or stringified output
- Please see the [`taskcrafter/plugins/`](taskcrafter/plugins/) directory on how plugins are defined. One of the basic examples is the [`echo`](taskcrafter/plugins/echo.py) plugin.
- You can also use external plugins, just name the plugin in jobs YAML file as `file:/path/to/plugin.py`, an example can be found in [`examples/jobs/external_plugin.yaml`](examples/jobs/external_plugin.yaml)

---

## 🕹️ CLI Usage

```bash
taskcrafter jobs list                   # List all jobs
taskcrafter jobs run                    # Execute all jobs
taskcrafter jobs run <job_id>           # Execute a specific job
taskcrafter jobs validate               # Validates jobs
taskcrafter plugins list                # Visualize job flow
taskcrafter plugins info <plugin_name>  # Show plugin info
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

- [ ] `depends_on`, `on_finish` etc. should support job params, not just IDs

      I am having 2nd thoughts on this, mainly because we can end in the loop of
      job under the job under the job under the job..

      I'll rethink the idea, if needed.

- [x] Automatically exit if no jobs are running
- [x] Add summary table report after run
- [x] `plugins info <name>` added. Will try to fetch docgen from the plugin file too.
- [x] Add `before_all`, `after_all`, `on_error`, `on_skip` global hooks
- [x] Support for job `input` and `output` resolution

      The output currently isn't required, since each plugin returns an item.
      This will always be saved in the .cache directory.

- [x] Validate if all jobs are defined correctly and reference to the existing plugin
- [x] The inputs now support templating with result, env and file
- [x] New plugin type: `terminate`

      Its called exit. For now, only string is being checked, no need for new
      PluginType Enum

- [x] Support for external plugins

      You can just name the plugin in jobs YAML file as `file:/path/to/plugin.py`.

      Please check the source code from the plugin before using it! I am not
      responsible for any issues caused by using external plugins.

- [ ] Docs: Document plugin dev best practices
- [ ] Add `--log-file` and `--log-level` CLI flag
- [ ] More unit tests, get to 100% code coverage 😊

---

## 📄 License

MIT License. Contributions welcome!

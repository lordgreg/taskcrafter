# TaskCrafter

🛠️ **TaskCrafter** – A modern, hackable task scheduler for developers.
Think *cron*, but smarter: YAML-defined jobs, plugin support, chaining logic, and easy extensibility.

---

### 🚀 Why TaskCrafter?

- ✅ Write jobs in YAML (not spaghetti shell scripts)
- 🔁 Chain tasks with conditions: `after_success`, `on_fail`, `depends_on`
- 🧩 Extend with Python plugins or shell scripts
- 📦 Git-friendly (keep jobs versioned alongside code)
- 🪄 CLI-first, DevOps-inspired

> Automate backups, notifications, scraping, dev tasks, server jobs... all in one place.


### Structure


taskcrafter/
├── taskcrafter/
│   ├── __init__.py
│   ├── cli.py              # glavni CLI vmesnik (click)
│   ├── engine.py           # job executor
│   ├── parser.py           # yaml parser
│   ├── plugin_loader.py    # dinamični plugin sistem
│   ├── scheduler.py        # logika odvisnosti in planiranja
│   └── logger.py           # barvni in strukturiran izpis
├── plugins/
│   ├── notify_slack.py     # primer plugina
│   ├── backup_s3.py
│   └── ...
├── jobs/
│   └── my_jobs.yaml        # uporabniška definicija jobov
├── examples/
│   ├── s3_backup.yaml
│   ├── db_snapshot.yaml
├── requirements.txt
├── README.md
└── setup.py

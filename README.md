# deep_learning

## SSH to a Raspberry Pi (`pi_ssh.py`)

Minimal SSH client for connecting to a Pi and running commands.

### Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # edit with your Pi's host, user, and key/password
```

### Usage

```bash
python pi_ssh.py               # interactive shell (type 'exit' to quit)
python pi_ssh.py "uptime"      # run a single command and exit
```

Configuration is read from environment variables (or a `.env` file):

| Variable      | Required | Description                              |
| ------------- | -------- | ----------------------------------------- |
| `PI_HOST`     | yes      | Hostname or IP of the Pi                  |
| `PI_USER`     | yes      | SSH username                              |
| `PI_PORT`     | no       | SSH port (default `22`)                   |
| `PI_KEY_PATH` | no       | Path to a private key file                |
| `PI_PASSWORD` | no       | Password, used if `PI_KEY_PATH` is unset  |

The Pi's host key must already be known to your system (e.g. via
`ssh-keyscan` or a prior `ssh` login) — the script rejects unknown hosts
rather than silently trusting them.

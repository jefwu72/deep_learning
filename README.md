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

## SSH MCP server (`ssh_mcp_server.py`)

An MCP server that lets any MCP client (Claude Code, Claude Desktop, etc.)
run commands on a remote host over SSH.

### Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # edit with your host, user, and key/password
```

`.env.example` uses `PI_*` variable names for `pi_ssh.py`; the MCP server
reads the equivalent `SSH_HOST` / `SSH_USER` / `SSH_PORT` / `SSH_KEY_PATH` /
`SSH_PASSWORD` names as per-call defaults. Set whichever names your client
uses, or omit them entirely and pass connection details as tool arguments
on each call.

### Running it

Directly, over stdio:

```bash
python ssh_mcp_server.py
```

Or auto-loaded by Claude Code via the included `.mcp.json`, which runs
`python3 ssh_mcp_server.py` in this directory.

### Tools

| Tool                 | Description                                                        |
| -------------------- | -------------------------------------------------------------------- |
| `ssh_run`             | Run a shell command on a remote host; returns stdout, stderr, exit code |
| `ssh_test_connection` | Verify SSH connectivity and auth without running a command           |

Each tool accepts optional `host`, `user`, `port`, `key_path`, and
`password` arguments that override the `SSH_*` environment defaults, so
one server instance can target multiple hosts.

As with `pi_ssh.py`, unknown host keys are rejected rather than
auto-trusted — the target host's key must already be in your
`known_hosts`.

**Note on secrets:** passing `password` as a tool argument puts it in the
MCP conversation/tool-call log. Prefer `key_path` (or environment-variable
defaults) over passing passwords through tool calls.

### Running on Android (Termux)

Runs the same way as any Linux box, inside [Termux](https://f-droid.org/packages/com.termux/)
(install from F-Droid, not Play Store — the Play Store build is unmaintained).

```bash
# 1. Base packages
pkg update && pkg upgrade
pkg install git python nodejs openssh

# 2. Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 3. Get this repo onto the phone
git clone <this-repo-url>
cd deep_learning
pip install -r requirements.txt

# 4. Get the key from shared storage (e.g. Downloads) into Termux's own home
termux-setup-storage        # one-time; grants access, creates ~/storage/downloads
mkdir -p ~/.ssh
cp ~/storage/downloads/pi_rsa ~/.ssh/pi_rsa
chmod 600 ~/.ssh/pi_rsa

# 5. Trust the host key once, from Termux itself (separate store from any
#    SSH app like JuiceSSH — those don't share known_hosts with Termux)
ssh -i ~/.ssh/pi_rsa <user>@<host>   # accept the fingerprint, then exit

# 6. Configure and launch
cp .env.example .env        # set SSH_HOST/SSH_USER, SSH_KEY_PATH=~/.ssh/pi_rsa
claude                      # auto-loads ssh_mcp_server.py via .mcp.json
```

If `pip install` fails building `cryptography` (a `paramiko`/`mcp` dependency),
install the prebuilt package instead: `pkg install python-cryptography`.

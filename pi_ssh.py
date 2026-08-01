#!/usr/bin/env python3
"""Minimal SSH client for connecting to a Raspberry Pi host.

Usage:
    python pi_ssh.py                # interactive shell (type 'exit' to quit)
    python pi_ssh.py "uptime"       # run one command and exit

Configuration is read from environment variables (see .env.example):
    PI_HOST       hostname or IP of the Pi (required)
    PI_USER       SSH username (required)
    PI_PORT       SSH port (default: 22)
    PI_KEY_PATH   path to a private key file (optional)
    PI_PASSWORD   password, used if PI_KEY_PATH is not set (optional)
"""
import os
import sys

import paramiko

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def connect() -> paramiko.SSHClient:
    host = os.environ.get("PI_HOST")
    user = os.environ.get("PI_USER")
    if not host or not user:
        sys.exit("PI_HOST and PI_USER must be set (see .env.example)")

    port = int(os.environ.get("PI_PORT", "22"))
    key_path = os.environ.get("PI_KEY_PATH")
    password = os.environ.get("PI_PASSWORD")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.load_system_host_keys()

    connect_kwargs = {"hostname": host, "port": port, "username": user}
    if key_path:
        connect_kwargs["key_filename"] = os.path.expanduser(key_path)
    elif password:
        connect_kwargs["password"] = password
    # else: rely on ssh-agent / default keys

    client.connect(**connect_kwargs)
    return client


def run_command(client: paramiko.SSHClient, command: str) -> int:
    stdin, stdout, stderr = client.exec_command(command)
    stdin.close()
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    if out:
        print(out, end="")
    if err:
        print(err, end="", file=sys.stderr)
    return stdout.channel.recv_exit_status()


def interactive(client: paramiko.SSHClient) -> None:
    print("Connected. Type 'exit' or 'quit' to close the session.")
    while True:
        try:
            command = input("pi$ ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if command.strip() in ("exit", "quit"):
            break
        if not command.strip():
            continue
        run_command(client, command)


def main() -> None:
    client = connect()
    try:
        if len(sys.argv) > 1:
            exit_code = run_command(client, " ".join(sys.argv[1:]))
            sys.exit(exit_code)
        else:
            interactive(client)
    finally:
        client.close()


if __name__ == "__main__":
    main()

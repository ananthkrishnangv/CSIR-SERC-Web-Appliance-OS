import subprocess
import time

vbox_dir = r"D:\Program Files\Oracle\VirtualBox"
vbox_c = rf"{vbox_dir}\VBoxC.dll"
vbox_svc = rf"{vbox_dir}\VBoxSVC.exe"
vbox_manage = rf"{vbox_dir}\VBoxManage.exe"

print("[*] Registering VBoxC.dll...")
res1 = subprocess.run(["regsvr32.exe", "/s", vbox_c], capture_output=True, text=True)
print("regsvr32 returncode:", res1.returncode)

print("[*] Running VBoxSVC.exe /ReRegServer...")
res2 = subprocess.run([vbox_svc, "/ReRegServer"], capture_output=True, text=True)
print("VBoxSVC returncode:", res2.returncode)

time.sleep(1)

print("[*] Testing VBoxManage.exe list vms...")
res3 = subprocess.run([vbox_manage, "list", "vms"], capture_output=True, text=True)
print("STDOUT:\n", res3.stdout)
print("STDERR:\n", res3.stderr)
print("RC:", res3.returncode)

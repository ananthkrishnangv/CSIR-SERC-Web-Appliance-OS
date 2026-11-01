import ctypes
from ctypes import wintypes
import winreg

advapi32 = ctypes.WinDLL("advapi32.dll")
RegOverridePredefKey = advapi32.RegOverridePredefKey
RegOverridePredefKey.restype = wintypes.LONG
RegOverridePredefKey.argtypes = [wintypes.HKEY, wintypes.HKEY]

HKEY_CLASSES_ROOT = wintypes.HKEY(0x80000000)
HKEY_CURRENT_USER = wintypes.HKEY(0x80000001)

# Open HKCU\Software\Classes
hkcu_classes = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes")
hkcu_classes_handle = wintypes.HKEY(hkcu_classes.handle)

print("[*] Redirecting HKEY_CLASSES_ROOT to HKCU\\Software\\Classes...")
err = RegOverridePredefKey(HKEY_CLASSES_ROOT, hkcu_classes_handle)
print("RegOverridePredefKey error code:", err)

if err == 0:
    # Now load VBoxProxyStub.dll and call DllRegisterServer
    try:
        print("[*] Loading VBoxProxyStub.dll...")
        proxy_dll = ctypes.WinDLL(r"D:\Program Files\Oracle\VirtualBox\VBoxProxyStub.dll")
        DllRegisterServer = proxy_dll.DllRegisterServer
        DllRegisterServer.restype = wintypes.HRESULT
        hr = DllRegisterServer()
        print("VBoxProxyStub DllRegisterServer HR:", hex(hr & 0xFFFFFFFF))
    except Exception as e:
        print("Exception registering VBoxProxyStub:", e)

    try:
        print("[*] Loading VBoxC.dll...")
        vbox_c = ctypes.WinDLL(r"D:\Program Files\Oracle\VirtualBox\VBoxC.dll")
        DllRegisterServer2 = vbox_c.DllRegisterServer
        DllRegisterServer2.restype = wintypes.HRESULT
        hr2 = DllRegisterServer2()
        print("VBoxC DllRegisterServer HR:", hex(hr2 & 0xFFFFFFFF))
    except Exception as e:
        print("Exception registering VBoxC:", e)

    # Restore HKCR
    RegOverridePredefKey(HKEY_CLASSES_ROOT, None)
    print("[*] Restored HKEY_CLASSES_ROOT.")

# Also register VBoxSVC.exe in HKCU
try:
    vbox_svc_path = r"D:\Program Files\Oracle\VirtualBox\VBoxSVC.exe"
    # VirtualBox CLSID: {B1A088A8-52BC-4c4f-9614-3A7A98F602A4} or {D2DE152C-451E-481D-901D-5A2172776D31}
    # Let's see what keys were created in HKCU\Software\Classes!
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\CLSID") as k:
        i = 0
        created = []
        while True:
            try:
                sub = winreg.EnumKey(k, i)
                created.append(sub)
                i += 1
            except OSError:
                break
        print(f"[*] Found {len(created)} CLSIDs registered in HKCU\\Software\\Classes\\CLSID!")
except Exception as e:
    print("Error inspecting HKCU CLSID:", e)

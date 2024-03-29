import subprocess

def find_usb_mount_points():
    try:
        result = subprocess.run(['lsblk', '-o', 'NAME,MOUNTPOINT', '-J'], capture_output=True, text=True)
        output = result.stdout

        devices = []
        if output:
            data = json.loads(output)
            for device in data.get('blockdevices', []):
                name = device.get('name')
                mountpoint = device.get('mountpoint')
                if mountpoint:
                    devices.append((name, mountpoint))

        return devices
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    usb_devices = find_usb_mount_points()
    for device in usb_devices:
        print(f"Device: {device[0]}, Mounted at: {device[1]}")

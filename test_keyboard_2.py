import hid
import time
import sys

# Gembird KB-G460 Vendor ID and Product ID
VENDOR_ID = 0x320F
PRODUCT_ID = 0x5055

# --- Captured USB Payloads ---
SEQUENCE_SET_RED = [
    bytes.fromhex("0432110b38000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff00"),
    bytes.fromhex("046a110b3838000000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff"),
    bytes.fromhex("04a40f0b387000000000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000"),
    bytes.fromhex("04da110b38a80000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff00"),
    bytes.fromhex("0412120b38e0000000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff"),
    bytes.fromhex("044d0f0b381801000000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000"),
    bytes.fromhex("047b110b30500100ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff00000000ff0000000000")
]

SEQUENCE_SET_BLUE = [
    bytes.fromhex("0433100b380000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000"),
    bytes.fromhex("046a110b38380000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff00"),
    bytes.fromhex("04a3100b3870000000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff000000"),
    bytes.fromhex("04db100b38a800000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000"),
    bytes.fromhex("0412120b38e00000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff00"),
    bytes.fromhex("044c100b3818010000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff000000"),
    bytes.fromhex("047a120b305001000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff00ff0000ff000000")
]


def find_control_interface(vid, pid):
    """Finds the specific vendor-defined interface for lighting control."""
    print(f"Searching for device VID={hex(vid)} PID={hex(pid)}...")
    devices = hid.enumerate(vid, pid)
    for device in devices:
        # The key is to find the "Vendor-Defined" usage page.
        # 0xFF00 to 0xFFFF is the range for vendor-defined pages.
        if device['usage_page'] >= 0xff00:
            print(f"Found a potential control interface:")
            print(f"  Path: {device['path'].decode('utf-8')}")
            print(f"  Usage Page: 0x{device['usage_page']:04x}")
            return device['path']
    return None

def send_sequence(device, sequence, name):
    """Sends a sequence of 7 packets to the HID device."""
    print(f"\nAttempting to send sequence for: {name}")
    try:
        for i, payload in enumerate(sequence):
            device.write(payload)
            print(f"  > Sent packet {i+1}/7")
            time.sleep(0.02)
        print(f"✅ Sequence '{name}' sent successfully!")
    except Exception as e:
        print(f"❌ Error sending sequence: {e}")

def main():
    """Main function to find the device and send commands."""
    device = None
    try:
        # Find the specific path of the lighting control interface
        device_path = find_control_interface(VENDOR_ID, PRODUCT_ID)

        if not device_path:
            print("\n❌ Error: Could not find the specific lighting control interface.")
            print("Please ensure the keyboard is plugged in and no other software is using it.")
            sys.exit(1)

        print("\n✅ Gembird KB-G460 control interface found! Connecting...")
        device = hid.device()
        device.open_path(device_path)
        
        print("✅ Connection successful!")
        device.set_nonblocking(1)

        print("\n--- Interactive Keyboard Control ---")
        print("Press Ctrl+C to exit.")

        while True:
            input("\nPress Enter to set keyboard color to RED...")
            send_sequence(device, SEQUENCE_SET_RED, "SET RED")

            input("\nPress Enter to set keyboard color to BLUE...")
            send_sequence(device, SEQUENCE_SET_BLUE, "SET BLUE")

    except IOError as ex:
        print(f"❌ {ex}")
        print("Error: Could not open device. Is another program using it?")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        if device:
            device.close()
            print("Device connection closed.")

if __name__ == '__main__':
    main()

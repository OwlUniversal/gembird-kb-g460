import hid
import time
import sys

# Gembird KB-G460 Vendor ID and Product ID
VENDOR_ID = 0x320F
PRODUCT_ID = 0x5055

# --- Captured USB Payloads ---
# Each payload is a 64-byte sequence. The Report ID (0x04) is the first byte.

# This sequence was captured when changing the color FROM GREEN TO RED
SEQUENCE_SET_RED = [
    bytes.fromhex("0432110b38000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff00"),
    bytes.fromhex("046a110b3838000000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff"),
    bytes.fromhex("04a40f0b387000000000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000"),
    bytes.fromhex("04da110b38a80000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff00"),
    bytes.fromhex("0412120b38e0000000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff"),
    bytes.fromhex("044d0f0b381801000000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000"),
    bytes.fromhex("047b110b30500100ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff00000000ff0000000000")
]

# This sequence was captured when changing the color FROM RED TO GREEN
SEQUENCE_SET_GREEN = [
    bytes.fromhex("0433100b380000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000"),
    bytes.fromhex("046a110b38380000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff00"),
    bytes.fromhex("04a3100b3870000000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff000000"),
    bytes.fromhex("04db100b38a800000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000"),
    bytes.fromhex("0412120b38e00000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff00"),
    bytes.fromhex("044c100b3818010000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff000000"),
    bytes.fromhex("047a120b305001000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff00ff0000ff000000")
]

def send_sequence(device, sequence, name):
    """Sends a sequence of 7 packets to the HID device."""
    print(f"\nAttempting to send sequence for: {name}")
    try:
        for i, payload in enumerate(sequence):
            device.write(payload)
            print(f"  > Sent packet {i+1}/7")
            time.sleep(0.02) # A small delay between packets is good practice
        print(f"✅ Sequence '{name}' sent successfully!")
    except Exception as e:
        print(f"❌ Error sending sequence: {e}")

def main():
    """Main function to find the device and send commands."""
    device = None
    try:
        print(f"Searching for device VID={hex(VENDOR_ID)} PID={hex(PRODUCT_ID)}...")
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        print("✅ Gembird KB-G460 keyboard found!")
        device.set_nonblocking(1)

        print("\n--- Interactive Keyboard Control ---")
        print("Press Ctrl+C to exit.")

        while True:
            input("\nPress Enter to set keyboard color to RED...")
            send_sequence(device, SEQUENCE_SET_RED, "SET RED")

            input("\nPress Enter to set keyboard color to GREEN...")
            send_sequence(device, SEQUENCE_SET_GREEN, "SET GREEN")

    except IOError as ex:
        print(f"❌ {ex}")
        print("Error: Keyboard not found or permission denied.")
        print("Please ensure the following:")
        print("1. The Gembird software is NOT running.")
        print("2. The keyboard is plugged in.")
        if sys.platform.startswith('linux'):
            print("3. You may need to run this script with 'sudo'.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        if device:
            device.close()
            print("Device connection closed.")

if __name__ == '__main__':
    main()

import hid
import time
import sys

# --- Device Configuration ---
VENDOR_ID = 0x320F
PRODUCT_ID = 0x5055

# --- The "Clean" Template Sequence (Captured from setting lights to OFF) ---
TEMPLATE_MASTER_SEQUENCE = [
    bytes.fromhex("0443000b380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"),
    bytes.fromhex("047b000b383800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"),
    bytes.fromhex("04b3000b387000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"),
    bytes.fromhex("04eb000b38a800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"),
    bytes.fromhex("0423010b38e000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"),
    bytes.fromhex("045c000b381801000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"),
    bytes.fromhex("048c000b305001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
]


def create_uniform_color_sequence(g, b, r): # Parameters updated for clarity
    """
    Generates the definitive 7-packet sequence for a uniform color.
    The hardware color format is GBR (Green, Blue, Red).
    """
    new_sequence = []
    color_triplet = [g, b, r] # Build the triplet in the correct GBR order

    for packet_template in TEMPLATE_MASTER_SEQUENCE:
        packet_list = list(packet_template)
        for i in range(8, 64, 3):
            if i + 2 < len(packet_list):
                packet_list[i:i+3] = color_triplet
        new_sequence.append(bytes(packet_list))
    
    return new_sequence


def find_control_interface(vid, pid):
    """Finds the specific vendor-defined interface for lighting control."""
    devices = hid.enumerate(vid, pid)
    for device in devices:
        if device['usage_page'] >= 0xff00:
            return device['path']
    return None

def send_sequence(device, sequence, name="Custom Color"):
    """Sends a complete 7-packet command sequence."""
    print(f"\nSending command: {name}")
    try:
        for i, payload in enumerate(sequence):
            device.write(payload)
            time.sleep(0.02)
        print("✅ Command sent successfully!")
    except Exception as e:
        print(f"❌ Error sending command: {e}")

def main():
    """Main function to find the device and run an interactive session."""
    device_path = find_control_interface(VENDOR_ID, PRODUCT_ID)

    if not device_path:
        print("❌ Error: Could not find the keyboard's lighting control interface.")
        sys.exit(1)

    print("✅ Gembird control interface found. Opening device...")
    
    device = None
    try:
        device = hid.device()
        device.open_path(device_path)
        print("✅ Connection successful!")

        print("\n--- Gembird KB-G460 ULTIMATE Color Control ---")
        print("Enter RGB color values (e.g., '255 0 255' for magenta).")
        print("Type 'exit' or press Ctrl+C to quit.")

        while True:
            try:
                user_input = input("\nEnter RGB color (0-255) > ").lower()
                if 'exit'.startswith(user_input):
                    break
                
                r_str, g_str, b_str = user_input.split()
                r, g, b = int(r_str), int(g_str), int(b_str)

                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    raise ValueError("Color values must be between 0 and 255.")

                # *** THIS IS THE FIX ***
                # We now pass the variables in the correct GBR order to the factory function.
                dynamic_sequence = create_uniform_color_sequence(g, b, r)
                
                send_sequence(device, dynamic_sequence, f"SET UNIFORM COLOR to (R={r}, G={g}, B={b})")

            except ValueError as e:
                print(f"Invalid input: {e}. Please enter three numbers separated by spaces (e.g., '0 128 255').")
            except Exception:
                print("Invalid input format. Please try again.")

    except (IOError, OSError) as ex:
        print(f"❌ Error: {ex}")
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        if device:
            device.close()
            print("\nDevice connection closed.")

if __name__ == '__main__':
    main()

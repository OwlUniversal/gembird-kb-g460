import hid
import time
import sys

# --- Device Configuration ---
VENDOR_ID = 0x320F
PRODUCT_ID = 0x5055

# --- Template Sequence ---
# We use a known-good sequence as a template. We will only change the color bytes.
# This is the sequence for RED (GRB color: 0, 255, 0)
TEMPLATE_SEQUENCE = [
    bytes.fromhex("0433100b380000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000"),
    bytes.fromhex("046a110b38380000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff00"),
    bytes.fromhex("04a3100b3870000000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff000000"),
    bytes.fromhex("04db100b38a800000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000"),
    bytes.fromhex("0412120b38e00000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff00"),
    bytes.fromhex("044c100b3818010000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000000000ff0000ff0000ff0000ff0000ff0000ff0000ff000000"),
    bytes.fromhex("047a120b305001000000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff0000ff00ff0000ff000000")
]


def create_color_sequence(g, r, b):
    """
    Generates a 7-packet sequence for a given color by modifying a template.
    Args:
        g (int): Green value (0-255)
        r (int): Red value (0-255)
        b (int): Blue value (0-255)
    Returns:
        list: A list of 7, 64-byte packets for the new color.
    """
    new_sequence = []
    for packet_template in TEMPLATE_SEQUENCE:
        # Convert the immutable `bytes` object to a mutable `list` of integers
        packet_list = list(packet_template)

        # The color data starts at Byte 8 and repeats in 3-byte chunks (GRB)
        # We loop through the packet and replace every color triplet.
        for i in range(8, 64, 3):
            # Check to make sure we don't write past the end of the packet
            if i + 2 < len(packet_list):
                packet_list[i] = b
                packet_list[i+1] = r
                packet_list[i+2] = g
        
        # Convert the list back to a `bytes` object and add it to our new sequence
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

        print("\n--- Gembird KB-G460 Dynamic Color Control ---")
        print("Enter RGB color values (e.g., '255 0 255' for magenta).")
        print("Press Ctrl+C to exit.")

        while True:
            try:
                user_input = input("\nEnter RGB color (0-255) > ")
                r_str, g_str, b_str = user_input.split()
                r, g, b = int(r_str), int(g_str), int(b_str)

                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    raise ValueError("Color values must be between 0 and 255.")

                # IMPORTANT: We pass the values in GRB order to the factory function!
                dynamic_sequence = create_color_sequence(g, r, b)
                
                send_sequence(device, dynamic_sequence, f"SET COLOR to (R={r}, G={g}, B={b})")

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
            print("Device connection closed.")

if __name__ == '__main__':
    main()

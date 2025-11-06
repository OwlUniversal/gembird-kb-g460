import hid
import time
import sys

# --- Device Configuration ---
VENDOR_ID = 0x320F
PRODUCT_ID = 0x5055

# --- The Definitive 3-Packet Command Structure ---

# Packet 1: Prepare for Static Color update.
COMMAND_PREPARE_STATIC = bytes.fromhex(
    "0401000100000000000000000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
)

# Packet 2: Color Data Template. We inject our RGB color here.
TEMPLATE_SET_COLOR_PROPERTIES = bytes.fromhex(
    "043503062100000000060404ff00ff00000300000000000000000000"
    "ff0000"  # <-- RGB COLOR at Bytes 28, 29, 30
    "00000000000000000000000000000000000000000000000000000000"
)

# Packet 3: Execute the update.
COMMAND_EXECUTE_UPDATE = bytes.fromhex(
    "0402000200000000000000000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
)


def create_true_static_color_sequence(r, g, b):
    """
    Constructs the full 3-packet sequence for setting a uniform static color.
    This mode uses standard RGB format.
    """
    # 1. Start with the "Prepare" packet.
    sequence = [COMMAND_PREPARE_STATIC]
    
    # 2. Create the "Color Data" packet.
    packet_list = list(TEMPLATE_SET_COLOR_PROPERTIES)
    # Inject the color at the correct offsets.
    packet_list[28] = r
    packet_list[29] = g
    packet_list[30] = b
    sequence.append(bytes(packet_list))
    
    # 3. Add the "Execute" packet.
    sequence.append(COMMAND_EXECUTE_UPDATE)
    
    return sequence


def find_control_interface(vid, pid):
    """Finds the specific vendor-defined interface for lighting control."""
    devices = hid.enumerate(vid, pid)
    for device in devices:
        if device['usage_page'] >= 0xff00:
            return device['path']
    return None

def send_command(device, command_sequence, name):
    """Sends a command sequence to the device."""
    print(f"\nSending command: {name}")
    try:
        for payload in command_sequence:
            device.write(payload)
            time.sleep(0.03) # A small delay for reliability
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

        print("\n--- Gembird KB-G460 TRUE Color Control ---")
        print("Enter RGB color values (e.g., '255 0 0' for red).")
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

                # Create the full 3-packet sequence.
                command_sequence = create_true_static_color_sequence(r, g, b)
                
                # Send the sequence.
                send_command(device, command_sequence, f"SET COLOR to (R={r}, G={g}, B={b})")

            except ValueError as e:
                print(f"Invalid input: {e}. Please enter three numbers separated by spaces.")
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

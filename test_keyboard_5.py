import hid
import time
import sys

# --- Device Configuration ---
VENDOR_ID = 0x320F
PRODUCT_ID = 0x5055

# --- The Ultimate Template Sequence (Captured from Per-Key Assignment) ---
# This sequence first clears all per-key effects, then applies a new color map.
# This ensures a truly uniform color.

# Packets 1-5: The "Prepare/Reset" command. Clears the "effect layer".
# Packet 6: The "Paint" command. This is where we'll write our color data.
# Packet 7: The "Commit" command. Applies the changes.
TEMPLATE_MASTER_SEQUENCE = [
    bytes.fromhex("0443000b380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"), # Pkt 1: Reset
    bytes.fromhex("047b000b383800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"), # Pkt 2: Reset
    bytes.fromhex("04b3000b387000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"), # Pkt 3: Reset
    bytes.fromhex("04eb000b38a800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"), # Pkt 4: Reset
    bytes.fromhex("0423010b38e000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"), # Pkt 5: Reset
    bytes.fromhex("045b010b381801000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"), # Pkt 6: Paint (we will fill this)
    bytes.fromhex("048c000b305001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")  # Pkt 7: Commit
]


def create_uniform_color_sequence(g, r, b):
    """Generates the definitive 7-packet sequence for a uniform color."""
    
    # Create the first 5 "reset" packets directly from the template
    new_sequence = list(TEMPLATE_MASTER_SEQUENCE[:5])
    
    # Create the 6th "paint" packet
    paint_packet_list = list(TEMPLATE_MASTER_SEQUENCE[5])
    color_triplet = [g, r, b]
    # Fill the entire color map (bytes 8-63) with the new color
    for i in range(8, 64, 3):
        if i + 2 < len(paint_packet_list):
            paint_packet_list[i:i+3] = color_triplet
    new_sequence.append(bytes(paint_packet_list))
    
    # Add the final "commit" packet
    new_sequence.append(TEMPLATE_MASTER_SEQUENCE[6])
    
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

                # IMPORTANT: We pass the values in GRB order to the factory function!
                dynamic_sequence = create_uniform_color_sequence(g, r, b)
                
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

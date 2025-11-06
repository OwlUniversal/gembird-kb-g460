import hid

# Your keyboard's VID and PID
VENDOR_ID = 0x320F
PRODUCT_ID = 0x5055

print("--- Searching for Gembird Keyboard Interfaces ---")
print(f"Looking for VID={hex(VENDOR_ID)}, PID={hex(PRODUCT_ID)}\n")

found_devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)

if not found_devices:
    print("❌ No Gembird devices found. Please check that it is plugged in.")
else:
    print(f"Found {len(found_devices)} matching interface(s). Details below:\n")
    for i, device_dict in enumerate(found_devices):
        print(f"--- Interface #{i} ---")
        # The 'path' is a unique identifier for this specific interface
        print(f"  Path: {device_dict['path'].decode('utf-8')}")
        print(f"  Interface Number: {device_dict['interface_number']}")
        print(f"  Product String: '{device_dict['product_string']}'")
        # Usage Page and Usage are key indicators for HID devices
        print(f"  Usage Page: 0x{device_dict['usage_page']:04x}")
        print(f"  Usage: 0x{device_dict['usage']:04x}")
        print("-" * 25)

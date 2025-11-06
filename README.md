# Reverse Engineering the Gembird KB-G460 Keyboard

This document details the successful journey of reverse engineering the USB protocol for the Gembird KB-G460 keyboard to achieve custom RGB lighting control. This project was a collaboration between the original researcher and Google's Gemini AI, driven by meticulous testing and data analysis.

The final result is a working Python script that can set a full-board, uniform static color, along with a complete understanding of the keyboard's unique lighting protocol and firmware features.

## Hardware Identifiers

*   **Vendor ID (VID):** `0x320F`
*   **Product ID (PID):** `0x5055`

## The Reverse Engineering Journey

Our path to success was iterative and required systematically solving several distinct problems:

1.  **Initial Failures:** Simple replay attacks of captured USB traffic failed, indicating a dynamic protocol that prevented basic playback.

2.  **Breakthrough 1: Finding the Control Interface:** We discovered the keyboard acts as a composite device with multiple HID interfaces. The key to communication was to stop trying to talk to the standard typing interface and instead connect directly to the **vendor-defined interface** (identifiable by a `Usage Page` of `0xff00` or higher). See `device_finder.py` for the diagnostic script used.

3.  **Breakthrough 2: The "Normal Mode" Protocol:** We found that the keyboard's software has different modes. The most stable and predictable protocol for static lighting is the "Normal" mode, accessible via the "All Light" button in the official software.

4.  **Breakthrough 3: The 3-Packet Command Structure:** Capturing the "All Light" command revealed a consistent three-packet sequence for setting a static color:
    *   **Packet 1: Prepare:** A command to put the keyboard in a state ready to receive a static color, clearing previous effects.
    *   **Packet 2: Data:** A complex packet containing the color information and other properties.
    *   **Packet 3: Execute:** A command to apply the new color.

5.  **Breakthrough 4 (The Final Key): Main Color vs. Indicator Color:** This was the most critical discovery. The data packet (Packet #2) contains **two separate color definitions**:
    *   **Main Color (Bytes 14, 15, 16):** Sets the color for the entire keyboard.
    *   **Win Lock Indicator Color (Bytes 28, 29, 30):** Sets the color that the `Win` key will display *if and only if* the hardware Win Lock is active.

## The Final Protocol

To set a uniform static color on the Gembird KB-G460:
1.  Connect to the vendor-defined HID interface.
2.  Send the 3-packet command sequence in order.
3.  The `Data` packet should be constructed from a known-good template, modifying **only the Main Color bytes (14, 15, 16)** to ensure predictable behavior and leave the Win Lock Indicator color at its default.

## Scripts & Usage

This repository contains the scripts used and developed during this research. The main control script is `normal_test_keyboard_6.py`.

**1. Install Dependencies:**
```bash
pip install hidapi
```

**2. Run the Control Script:**
Before running, ensure the official Gembird software is completely closed.
```bash
python normal_test_keyboard_6.py
```
The script will connect to the keyboard and prompt you to enter RGB values to change the color.

**3. Debugging:**
If the script has trouble finding the keyboard on your system, you can use `device_finder.py` to list all available HID interfaces for the device and verify the connection path.

## Known Firmware Quirks

### The "Win Lock" Indicator
The keyboard's `Win` key LED serves a dual purpose. Its color is controlled separately from the rest of the keyboard.

*   **Behavior:** The script sets the main keyboard color. The `Win` key's color is set independently and indicates the status of the Win Lock function. Our script uses a known-good template that sets this indicator color to a default (Red).
*   **Control:** The Win Lock function (and thus the Win key's light) can only be toggled using the hardware key combination **`Fn + Win Key`**. Pressing this will switch the Win key between displaying its indicator color and matching the main color set by the script. This is the intended operation.

## Future Contributions

This project successfully decoded the static color protocol. Future work could include:
*   **Decoding Brightness and Speed:** Capturing traffic while changing the "Brightness" and "Speed" sliders to find their corresponding bytes in the data packet.
*   **Decoding Other Effects:** Systematically capturing the command sequences for other built-in effects ("Breathing", "Rainbow", etc.) to map out their command IDs.
*   **Full `Data` Packet Mapping:** Reverse engineering all the "unknown" bytes in the data packet to allow full control over all features, including the Win Lock indicator color.
*   **Building a GUI:** Creating a graphical user interface to control the keyboard's lighting without using the command line.

## Acknowledgments
This research was conducted by the original poster with the iterative assistance of Google's Gemini AI. The success of this project is a testament to the power of persistent, methodical testing.

## License
This project is licensed under the MIT License.

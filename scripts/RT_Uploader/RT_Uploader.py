#!/usr/bin/env python3
import serial.tools.list_ports
import subprocess
import sys
import requests
import os

def get_latest():
    url = "https://rosscoe.com/files/RT_EX-Turntable.latest.hex"
    response = requests.get(url)
    # Save the content in binary mode
    with open("RT_EX-Turntable.latest.hex", "wb") as f:
        f.write(response.content)
    return response.status_code


def find_nano_port():
    """Finds potential Arduino Nano ports by checking USB Vendor/Product IDs."""
    # Common VID:PID for Nano: 0403:6001 (FTDI) or 1a86:7523 (CH340)
    nano_ids = ["0403:6001", "1a86:7523"]
    ports = serial.tools.list_ports.comports()

    for port in ports:
        if any(id in port.hwid.lower() for id in nano_ids):
            return port.device
    return None

def upload_to_nano(port, hex_file, baud=115200):
    """Executes avrdude to flash the hex file."""
    # Use 115200 for new Nano bootloaders, 57600 for old ones
    cmd = [
        "avrdude",
        "-v",
        "-p", "atmega328p",
        "-c", "arduino",
        "-P", port,
        "-b", str(baud),
        "-D",
        f"-Uflash:w:{hex_file}:i"
    ]

    print(f"Attempting upload to {port}...")
    try:
        subprocess.run(cmd, check=True)
        print("Upload Successful!")
    except subprocess.CalledProcessError:
        print("Upload failed. If 'programmer is not responding', try baud rate 57600.")

if __name__ == "__main__":

    code = get_latest()
    if code == 200:
        hex_path = "./RT_EX-Turntable.latest.hex"
        nano_port = find_nano_port()

        if nano_port:
            upload_to_nano(nano_port, hex_path)
        else:
            print("No Arduino Nano detected.")
        os.remove(hex_path)
    else:
        print("Could not get latest RT_EX-Turntable")


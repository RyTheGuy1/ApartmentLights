import usb.core
import usb.util
import time
import os
import requests
import configparser

# Morse code dictionary
MORSE_CODE = {'S': '...', 'O': '---'}

# Function to blink the light in morse code for SOS
def morse_code_sos(device):
    for char in "SOS":
        code = MORSE_CODE[char]
        for symbol in code:
            if symbol == '.':
                blink_light(device, 0.5)  # Short blink for dot
            elif symbol == '-':
                blink_light(device, 1.5)  # Long blink for dash
            time.sleep(0.5)  # Space between parts of the same letter
        time.sleep(1.5)  # Space between different letters

# Function to blink the light
def blink_light(device, duration):
    device.ctrl_transfer(0x40, 0x01)  # Example to turn on
    time.sleep(duration)
    device.ctrl_transfer(0x40, 0x00)  # Example to turn off
    time.sleep(duration)

# Function to ping the cloud server
def ping_server(domain):
    try:
        response = requests.get(domain)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Function to update the .conf file
def update_conf_file(config_file, vendor_id, product_id):
    config = configparser.ConfigParser()
    config.read(config_file)
    config.set('DEFAULT', 'LightVendorId', vendor_id)
    config.set('DEFAULT', 'LightProductId', product_id)
    
    with open(config_file, 'w') as configfile:
        config.write(configfile)

# Load configuration from .conf file
config_file = 'config.conf'
config = configparser.ConfigParser()
config.read(config_file)

light_vendor_id = config.get('DEFAULT', 'LightVendorId')
light_product_id = config.get('DEFAULT', 'LightProductId')
domains = config.get('DEFAULT', 'Domains').split(',')
ping_interval = int(config.get('DEFAULT', 'PingInterval'))

# Find USB device
device = usb.core.find(idVendor=int(light_vendor_id, 16), idProduct=int(light_product_id, 16))

# If device not found, prompt user to select from list of devices
if device is None:
    print("Specified USB device not found.")
    devices = usb.core.find(find_all=True)
    
    for i, dev in enumerate(devices):
        print(f"{i}: Vendor ID = {hex(dev.idVendor)}, Product ID = {hex(dev.idProduct)}")

    selection = int(input("Select the USB device (number): "))
    selected_device = list(usb.core.find(find_all=True))[selection]
    
    light_vendor_id = hex(selected_device.idVendor)
    light_product_id = hex(selected_device.idProduct)
    
    update_conf_file(config_file, light_vendor_id, light_product_id)
    device = selected_device

# Detach kernel driver if necessary
if device.is_kernel_driver_active(0):
    device.detach_kernel_driver(0)

# Set configuration
device.set_configuration()

# Main loop to ping server and control the light
try:
    while True:
        is_online = ping_server(domains[0])  # Using the first domain in the list
        if is_online:
            print("Server is online. Keeping light stable.")
            # Keep USB power stable (no blinking)
        else:
            print("Server is offline. Blinking SOS.")
            morse_code_sos(device)
        
        time.sleep(ping_interval)
except KeyboardInterrupt:
    usb.util.dispose_resources(device)
    print("Program stopped.")

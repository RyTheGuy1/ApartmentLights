import usb.core
import usb.util
import configparser
import os

# Get the directory of the current script (root/src/)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the config file in the root directory (root/light_config.conf)
config_file = os.path.join(script_dir, '..', 'light_config.conf')

# Load the configuration file
config = configparser.ConfigParser()

# Check if the config file exists
if os.path.exists(config_file):
    config.read(config_file)
else:
    # If the config file doesn't exist, initialize a default config
    config['DEFAULT'] = {}

# Try to get ProductID from the config file
light_product_id = config.get('DEFAULT', 'LightProductId', fallback=None)

# If ProductID exists in the conf file, skip the selection process
if light_product_id:
    print(f"ProductID {light_product_id} already exists in the configuration. Skipping device selection.")
else:
    # Find all connected USB devices
    devices = list(usb.core.find(find_all=True))

    # If no USB devices are found
    if not devices:
        print("No USB devices found.")
        exit()

    # Display USB devices with index for user to select
    print("Select the USB device by index:")
    for index, device in enumerate(devices, start=1):
        print(f"{index}: VendorID = {hex(device.idVendor)}, ProductID = {hex(device.idProduct)}")

    # Ask user to select a USB device
    try:
        selected_index = int(input("Enter the index of the device you want to select: ")) - 1

        # Ensure the selected index is valid
        if selected_index < 0 or selected_index >= len(devices):
            print("Invalid index. Please run the script again.")
            exit()

        # Get the selected device's ProductID
        selected_device = devices[selected_index]
        selected_product_id = hex(selected_device.idProduct)

        # Update config file with the selected ProductID
        config.set('DEFAULT', 'LightProductId', selected_product_id)

        # Write changes to the configuration file
        with open(config_file, 'w') as configfile:
            config.write(configfile)

        print(f"ProductID {selected_product_id} has been saved to {config_file}.")

    except ValueError:
        print("Invalid input. Please enter a number corresponding to the device index.")

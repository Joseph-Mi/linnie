FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

# Ensure the target kernel supports mounting RAUC bundles.
# (RAUC bundles are squashfs images mounted through a loop device.)
# SRC_URI:append = " file://rauc-squashfs.cfg"

# Enable all CM4 peripheral drivers (cameras, I2C, SPI, GPIO, USB, PCIe, etc.)
SRC_URI:append = " file://cm5-peripherals.cfg"

# Enable Raspberry Pi libcamera pipeline requirements (ISP + codec + media controller)
# SRC_URI:append = " file://rpi-libcamera-isp.cfg"

# Enable Bluetooth support
SRC_URI:append = " file://bluetooth.cfg"

# Enable USB HID Support (keyboard, mouse)
SRC_URI:append = " file://usb-hid.cfg"

# Enable USB Camera (UVC) Support (Logitech C920x, etc.)
SRC_URI:append = " file://usb-camera.cfg"
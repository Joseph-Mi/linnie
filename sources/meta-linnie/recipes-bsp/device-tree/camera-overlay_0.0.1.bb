SUMMARY = "Camera device tree overlay for Linnie"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

# Compatible with both base rpi5 and our custom machine
COMPATIBLE_MACHINE = "^rpi$|raspberrypi5|cm5-mi450-linnie"

inherit devicetree

SRC_URI = "file://camera-overlay.dts"

S = "${WORKDIR}"

do_compile() {
    # Compile the device tree overlay
    dtc -@ -I dts -O dtb -o camera-overlay.dtbo ${WORKDIR}/camera-overlay.dts
}

do_install() {
    # Install to the overlays directory
    install -d ${D}/boot/overlays
    install -m 0644 camera-overlay.dtbo ${D}/boot/overlays/
}

FILES:${PN} = "/boot/overlays/camera-overlay.dtbo"

SUMMARY = "TMP100 Temperature Sensor Overlay for CM5 MI450 Linnie"
DESCRIPTION = "Device tree overlay for 6x TMP100 sensors on I2C1"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

COMPATIBLE_MACHINE = "^rpi$|raspberrypi5|cm5-mi450-linnie"

inherit devicetree

SRC_URI = "file://thermal-overlay.dts"

S = "${WORKDIR}"

do_compile() {
    dtc -@ -I dts -O dtb -o thermal-overlay.dtbo ${WORKDIR}/thermal-overlay.dts
}

do_install() {
    install -d ${D}/boot/overlays
    install -m 0644 thermal-overlay.dtbo ${D}/boot/overlays/
}

FILES:${PN} = "/boot/overlays/thermal-overlay.dtbo"

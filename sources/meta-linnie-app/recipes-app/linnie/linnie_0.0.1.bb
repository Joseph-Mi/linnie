SUMMARY = "Linnie System Services for CM5 MI450"
DESCRIPTION = "Python services for thermal monitoring and USB camera on CM5 MI450 carrier board"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://setup.py \
    file://linnie/__init__.py \
    file://linnie/thermal.py \
    file://linnie/camera.py \
    file://linnie-thermal.service \
    file://linnie-camera.service \
"

S = "${WORKDIR}"

inherit setuptools3 systemd

# Runtime dependencies
RDEPENDS:${PN} += " \
    python3-core \
    python3-logging \
    v4l-utils \
"

# Optional: ffmpeg for camera recording (uncomment when needed)
# RDEPENDS:${PN} += "ffmpeg"

# Systemd services
SYSTEMD_SERVICE:${PN} = "linnie-thermal.service linnie-camera.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install:append() {
    # Install systemd services
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/linnie-thermal.service ${D}${systemd_system_unitdir}/
    install -m 0644 ${WORKDIR}/linnie-camera.service ${D}${systemd_system_unitdir}/

    # Create recording directory (will be owned by root)
    install -d ${D}/var/lib/linnie/recordings
}

FILES:${PN} += " \
    ${systemd_system_unitdir}/linnie-thermal.service \
    ${systemd_system_unitdir}/linnie-camera.service \
    /var/lib/linnie \
"

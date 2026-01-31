SUMMARY = "linnie application for keyboard functionality, digital camera, and linux OS"
DESCRIPTION = "Python application for USB camera, telemetry, and keyboard functionality on Linux OS"
LICENSE = "CLOSED"

FILESEXTRAPATHS:prepend := "${THISDIR}/../../..:"

SRC_URI = ""

S = "${WORKDIR}/application"

# Only minimal Python

RDEPENDS:${PN} += ""


inherit setuptools3 systemd

SYSTEMD_SERVICE:${PN} = "dvr.service"
SYSTEMD_AUTO_ENABLE = "enable"

DEPENDS += "protobuf-native"

do_compile:prepend() {
    # Compile any protobufs present in the app tree
    proto_files=$(find ${S} -name "*.proto")

    if [ -n "${proto_files}" ]; then
        for proto in ${proto_files}; do
            proto_dir=$(dirname ${proto})
            proto_name=$(basename ${proto})
            (cd ${proto_dir} && ${STAGING_BINDIR_NATIVE}/protoc --python_out=. ${proto_name})
        done
    fi
}

do_install:append() {
    # Install systemd service
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/meta-dvr/recipes-app/dvr/files/dvr.service ${D}${systemd_system_unitdir}/

    # Ship default DVR config into /config on the image
    install -d ${D}/config
    cp -r ${S}/src/dvr/config/. ${D}/config/

    # Ship sandbox helper into /scripts on the image
    install -d ${D}/scripts
    install -m 0644 ${S}/src/dvr/sandbox.py ${D}/scripts/
}

FILES:${PN} += ""

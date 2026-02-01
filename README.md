# Linnie

Custom embedded Linux distribution for CM5 MI450 based on Yocto/Poky.

## Prerequisites

- Docker Desktop with WSL2
- VS Code with Dev Containers extension
- At least 250GB free disk space
- 16GB+ RAM recommended

## Getting Started

1. **Clone the repository:**
```bash
git clone --recurse-submodules https://github.com/yourname/linnie.git
cd linnie
```

2. **Open in VS Code:**
```bash
code .
```
Then select "Reopen in Container" when prompted.

## Building with KAS

Inside the devcontainer, use KAS to build:

```bash
# Build the Default image
kas build kas/linnie.yml

# Different Builds
kas build kas/linnie.yml -- -c build core-image-minimal
kas build kas/linnie.yml -- -c build core-image-base
#Build with Specific Recipe to Isolate Issues
kas shell kas/linnie.yml -c "bitbake thermal-overlay"
kas shell kas/linnie.yml -c "bitbake linnie"

# Or build with shell access for debugging
kas shell /workspaces/linnie/kas/linnie.yml
bitbake core-image-base
bitbake core-image-minimal
```

The build output will be in `build/tmp/deploy/images/cm5-mi450-linnie/`.

### Build with Bitbake
1. Show All Current Layers:
```bash
	bitbake-layers show-layers
```
2. Explore to Learn What KAS did:
```bash
	cat conf/local.conf
	cat conf/bblayers.conf
	bitbake -e | grep "^MACHINE=" # what machine is set
	bitbake-layers show-recipes "*-image-*" # what avail images to build
```
3. Building The Image:
```bash
	bitbake core-image-base # suggested image by KAS
	bitbake core-image-minimal # minimal image (smaller)
```
4. Clean Specific Recipes or Everything if Build Fails:
```bash
	bitbake -c cleanall <recipe-name>
	bitbake <recipe-name>

	bitbake -c cleanall core-image-base
	bitbake core-image-base
```
5. Check Disk Space:
```bash
	df -h /yocto
```

## Project Structure

```
linnie/
├── .devcontainer/       # Dev container configuration
├── conf/
│   └── site.conf        # Site-specific build settings
├── kas/
│   └── linnie.yml       # KAS build configuration
├── scripts/             # Utility scripts
└── sources/
    ├── meta-linnie/     # Custom layer (machine, distro, recipes)
    ├── meta-openembedded/
    ├── meta-raspberrypi/
    └── poky/
```

## Customizing the Build

- **Machine config**: `sources/meta-linnie/conf/machine/cm5-mi450-linnie.conf`
- **Distro config**: `sources/meta-linnie/conf/distro/linnie.conf`
- **Build settings**: `conf/site.conf`
- **KAS config**: `kas/linnie.yml`

## Adding Custom Recipes

Create recipes in `sources/meta-linnie/recipes-*/`:

```bash
mkdir -p sources/meta-linnie/recipes-apps/myapp
# Add myapp_1.0.bb recipe file
```

## SSH For Remote Network Access

## Running Docker Container

## U-Boot Bootloader

## Modifying U-Boot Environment

## Runtime Package Management

## After Building Successfully

### Finding Your Build Output

Once the build completes successfully, your bootable image and related files are located at:
```bash
/yocto/build/tmp/deploy/images/raspberrypi5/
```

#### Key Output Files
```bash
# View all output files
ls /yocto/build/tmp/deploy/images/raspberrypi5/

# Key files you'll see:
core-image-minimal-raspberrypi5.rootfs.wic.bz2     ← Bootable SD card image (compressed)
core-image-minimal-raspberrypi5.rootfs.wic.bmap    ← Block map for fast flashing
core-image-minimal-raspberrypi5.rootfs.manifest    ← List of installed packages
Image-raspberrypi5.bin                             ← Linux kernel
bcm2712-rpi-5-b.dtb                               ← Device tree blob
bootfiles/                                         ← Bootloader files (config.txt, etc.)
modules-*.tgz                                      ← Kernel modules archive
```

#### Check Your Image
```bash
# Find the bootable image
ls /yocto/build/tmp/deploy/images/raspberrypi5/*.wic.bz2

# Example output:
# /yocto/build/tmp/deploy/images/raspberrypi5/core-image-minimal-raspberrypi5.rootfs-20260131184059.wic.bz2
# /yocto/build/tmp/deploy/images/raspberrypi5/core-image-minimal-raspberrypi5.rootfs.wic.bz2 -> (symlink to timestamped file)

# Check image size
ls -lh /yocto/build/tmp/deploy/images/raspberrypi5/*.wic.bz2

# Expected size: ~40-60MB compressed (minimal), ~100-150MB (base), larger (custom)
```

#### View Installed Packages
```bash
# See what's included in your image
cat /yocto/build/tmp/deploy/images/raspberrypi5/core-image-minimal-raspberrypi5.rootfs.manifest

# You'll see packages like:
# - linux-raspberrypi (kernel)
# - busybox (core utilities)
# - systemd (init system)
# - dropbear (SSH server)
# - base-files, util-linux, etc.
```

---

### Flashing the Image to SD Card

You have several options for flashing your image to a microSD card:

#### Option 1: Flash from DevContainer (Linux Tools)

**Using dd (traditional method):**
```bash
# 1. Decompress the image
cd /yocto/build/tmp/deploy/images/raspberrypi5/
bunzip2 -k core-image-minimal-raspberrypi5.rootfs.wic.bz2
# Creates: core-image-minimal-raspberrypi5.rootfs.wic

# 2. Insert SD card and find device name
lsblk
# Look for your SD card (e.g., /dev/sdb or /dev/mmcblk0)

# 3. Flash to SD card
# WARNING: This ERASES the SD card! Double-check the device name!
sudo dd if=core-image-minimal-raspberrypi5.rootfs.wic \
        of=/dev/sdX \
        bs=4M \
        status=progress \
        && sync

# Replace /dev/sdX with your actual SD card device
```

**Using bmaptool (faster, recommended):**
```bash
# Flash compressed image directly (no need to decompress)
sudo bmaptool copy \
  core-image-minimal-raspberrypi5.rootfs.wic.bz2 \
  /dev/sdX

# bmaptool only writes used blocks, making it much faster than dd
```

#### Option 2: Flash from Windows

**Step 1: Copy image to Windows**
```bash
# From DevContainer terminal
cp /yocto/build/tmp/deploy/images/raspberrypi5/core-image-minimal-raspberrypi5.rootfs.wic.bz2 \
   /workspaces/linnie/

# The file is now accessible at:
# C:\Users\YourName\path\to\linnie\core-image-minimal-raspberrypi5.rootfs.wic.bz2
```

**Step 2: Decompress**
- Right-click the `.wic.bz2` file
- Use 7-Zip or similar to extract
- You'll get a `.wic` file

**Step 3: Flash using Raspberry Pi Imager**
1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Open Raspberry Pi Imager
3. Choose "Use custom" image
4. Select your `.wic` file
5. Choose your SD card
6. Click "Write"

**Alternative: Win32DiskImager**
1. Download [Win32DiskImager](https://sourceforge.net/projects/win32diskimager/)
2. Select your `.wic` file
3. Select SD card drive
4. Click "Write"

#### Option 3: Flash from Another Linux Machine
```bash
# Copy image to remote machine via SCP
scp /yocto/build/tmp/deploy/images/raspberrypi5/core-image-minimal-raspberrypi5.rootfs.wic.bz2 \
    user@remotemachine:/tmp/

# SSH to remote machine
ssh user@remotemachine

# Flash from remote machine
cd /tmp
bunzip2 core-image-minimal-raspberrypi5.rootfs.wic.bz2
sudo dd if=core-image-minimal-raspberrypi5.rootfs.wic of=/dev/sdX bs=4M status=progress && sync
```

---

### Booting Your CM5

#### Hardware Setup

1. **Insert SD card** into CM5 carrier board
2. **Connect peripherals** (if testing):
   - HDMI cable to monitor (optional)
   - USB keyboard (optional)
   - Ethernet cable (optional, for network access)
   - Serial console cable (optional, for debugging)
3. **Apply power** (5V, 3A recommended)

#### First Boot

The system should boot in **15-30 seconds**. You'll see:
- Bootloader messages
- Kernel boot messages
- systemd starting services
- Login prompt

#### Default Login Credentials
```
Login: root
Password: (just press Enter - no password)
```

**Note:** Empty root password and SSH access are enabled because the image was built with `debug-tweaks` feature. **Do not use this in production!**

#### Verify Your System
```bash
# Check kernel version
uname -a

# Check system info
cat /etc/os-release

# Check available disk space
df -h

# Check running services
systemctl status

# Check network interfaces
ip addr show

# Test SSH (if Ethernet connected)
# From your PC: ssh root@<cm5-ip-address>
```

---

### Building the Full Image (core-image-base)

Now that you've successfully built `core-image-minimal`, you can build the fuller `core-image-base` which includes:
- Package management tools
- More networking utilities
- Development tools
- Additional system utilities
```bash
# Exit current shell (if in one)
exit

# Enter KAS shell
kas shell /workspaces/linnie/kas/linnie.yml

# Build core-image-base
bitbake core-image-base

# Expected build time: 30-60 minutes
# Most packages are already built and cached, so this is much faster!
```

Or change the target in `kas/linnie.yml`:
```yaml
# Edit kas/linnie.yml
target: core-image-base  # Changed from core-image-minimal
```

Then rebuild:
```bash
kas build /workspaces/linnie/kas/linnie.yml
```

---

### Customizing Your Image

#### Adding Packages to Your Image

Edit your image recipe or create a custom one:
```bash
# Create a custom image recipe
mkdir -p /workspaces/linnie/sources/meta-linnie/recipes-core/images
nano /workspaces/linnie/sources/meta-linnie/recipes-core/images/linnie-image.bb
```

**Example custom image:**
```bitbake
SUMMARY = "Custom Linnie Image for CM5"
LICENSE = "MIT"

inherit core-image

# Include everything from core-image-base
require recipes-core/images/core-image-base.bb

# Add custom packages
IMAGE_INSTALL:append = " \
    htop \
    vim \
    tmux \
    git \
    python3 \
    python3-pip \
    i2c-tools \
    spi-tools \
"

# Add extra features
IMAGE_FEATURES:append = " \
    package-management \
    ssh-server-dropbear \
"

# Set root password (for production)
# EXTRA_USERS_PARAMS = "usermod -P 'yourpassword' root;"
```

Then build your custom image:
```bash
bitbake linnie-image
```

#### Adding Kernel Modules
```bash
# Create kernel modification
mkdir -p /workspaces/linnie/sources/meta-linnie/recipes-kernel/linux/files

# Add device tree overlay
nano /workspaces/linnie/sources/meta-linnie/recipes-kernel/linux/files/my-overlay.dts

# Add kernel bbappend
nano /workspaces/linnie/sources/meta-linnie/recipes-kernel/linux/linux-raspberrypi_%.bbappend
```

**Example bbappend:**
```bitbake
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:append = " \
    file://my-overlay.dts \
"

do_compile:append() {
    # Compile device tree overlay
    dtc -@ -I dts -O dtb -o ${B}/my-overlay.dtbo ${WORKDIR}/my-overlay.dts
}

do_deploy:append() {
    install -d ${DEPLOYDIR}/overlays
    install -m 0644 ${B}/my-overlay.dtbo ${DEPLOYDIR}/overlays/
}
```

---

### Cleaning and Rebuilding

#### Clean Specific Recipe
```bash
# Clean a specific package
bitbake -c cleanall linux-raspberrypi

# Rebuild
bitbake linux-raspberrypi
```

#### Clean Entire Build
```bash
# Remove build artifacts (keeps downloads and sstate)
rm -rf /yocto/build/tmp

# Rebuild
bitbake core-image-minimal
```

#### Start Completely Fresh
```bash
# WARNING: This deletes all Docker volumes!
exit  # Exit container first

# In VS Code terminal (outside container)
docker volume rm linnie-yocto-build
docker volume rm linnie-yocto-workspace
# Keep downloads and sstate to speed up rebuild:
# docker volume rm linnie-yocto-downloads
# docker volume rm linnie-yocto-sstate

# Rebuild container
# F1 → "Dev Containers: Rebuild Container"
```

---

### Build Statistics and Troubleshooting

#### Check Build Statistics
```bash
# Build time per recipe
cat /yocto/build/tmp/buildstats/*/build_stats

# Disk usage breakdown
du -sh /yocto/downloads/        # Source tarballs
du -sh /yocto/sstate-cache/     # Compiled cache
du -sh /yocto/build/tmp/        # Build artifacts
```

#### Common Issues

**Out of disk space:**
- Increase Docker disk allocation (Docker Desktop → Settings → Resources)
- Clean old builds: `rm -rf /yocto/build/tmp`

**Build fails after host update:**
- Rebuild container: `F1` → "Dev Containers: Rebuild Container"

**Package fetch fails:**
- Check network: `ping github.com`
- Check DNS: `cat /etc/resolv.conf`
- Retry: `bitbake <recipe-name>`

**Permission errors:**
```bash
sudo chown -R vscode:vscode /yocto
```

---

# Lessons Learned
1. instead of manually creating toolbox via source oe-init-build-env, KAS can run overall bitbake commands, pull correct repositories, and create my dev env
2. KAS will no longer need my submodules for poky, openembedded, and BSP layers as submodules (submodules checkout specific commits (detached HEAD), KAS expects to manage branches and update repos, but KAS can't find branch "scarthgap" with the detached HEAD)
3. Opening a project from Windows into a DevContainer mounts it as an NTFS (9p) filesystem, which breaks Yocto due to lack of case sensitivity, poor symlink/hard-link support, and slow I/O. The fix was to keep editable source files on the Windows-mounted workspace but move Yocto-generated files (build, downloads, sstate, cloned layers) onto Linux-backed Docker volumes (or fully into WSL2’s ext4 filesystem). I chose to do this instead of moving all to WSL since im broke (no build machine) AND this makes it more production like so anyone can just clone and use and not have to clone into their wsl (this may just be a persional bias as I rarely do this). 
4. PR is commit-based lol

For more information:
- [Yocto Project Documentation](https://docs.yoctoproject.org/)
- [meta-raspberrypi Layer](https://github.com/agherzan/meta-raspberrypi)
- [BitBake User Manual](https://docs.yoctoproject.org/bitbake/)
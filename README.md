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
# Build the default image
kas build /workspaces/linnie/kas/linnie.yml

# Or build with shell access for debugging
kas shell /workspaces/linnie/kas/linnie.yml
bitbake core-image-base
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


# Lessons Learned
1. instead of manually creating toolbox via source oe-init-build-env, KAS can run overall bitbake commands, pull correct repositories, and create my dev env
2. KAS will no longer need my submodules for poky, openembedded, and BSP layers as submodules (submodules checkout specific commits (detached HEAD), KAS expects to manage branches and update repos, but KAS can't find branch "scarthgap" with the detached HEAD)
3. Opening a project from Windows into a DevContainer mounts it as an NTFS (9p) filesystem, which breaks Yocto due to lack of case sensitivity, poor symlink/hard-link support, and slow I/O. The fix was to keep editable source files on the Windows-mounted workspace but move Yocto-generated files (build, downloads, sstate, cloned layers) onto Linux-backed Docker volumes (or fully into WSL2’s ext4 filesystem). I chose to do this instead of moving all to WSL since im broke (no build machine) AND this makes it more production like so anyone can just clone and use and not have to clone into their wsl (this may just be a persional bias as I rarely do this). 
4. PR is commit-based lol
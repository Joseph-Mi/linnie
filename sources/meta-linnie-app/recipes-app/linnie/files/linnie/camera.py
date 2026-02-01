#!/usr/bin/env python3
"""
Linnie Camera Service

Provides USB camera (UVC) functionality:
- Video device management (/dev/video*)
- Recording to storage on demand
- Integration with video calling platforms (exposes as V4L2 device)

Uses V4L2 (Video4Linux2) for camera access.
The Logitech C920x appears as a standard UVC device.
"""

import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('linnie-camera')


@dataclass
class CameraDevice:
    """Represents a video capture device."""
    path: str
    name: str
    driver: str
    capabilities: List[str]


# Recording configuration
RECORDING_DIR = Path('/var/lib/linnie/recordings')
DEFAULT_RESOLUTION = (1920, 1080)  # C920x supports 1080p
DEFAULT_FRAMERATE = 30
DEFAULT_FORMAT = 'mp4'


class CameraManager:
    """Manages USB camera devices and recording."""

    def __init__(self):
        self.running = True
        self.cameras: List[CameraDevice] = []
        self.active_recording: Optional[subprocess.Popen] = None
        self._ensure_recording_dir()

    def _ensure_recording_dir(self):
        """Create recording directory if it doesn't exist."""
        RECORDING_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Recording directory: {RECORDING_DIR}")

    def discover_cameras(self) -> List[CameraDevice]:
        """Discover available video devices."""
        self.cameras = []
        video_devices = Path('/dev').glob('video*')

        for device_path in sorted(video_devices):
            try:
                # Use v4l2-ctl to get device info
                result = subprocess.run(
                    ['v4l2-ctl', '-d', str(device_path), '--info'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    info = result.stdout
                    name = self._parse_field(info, 'Card type')
                    driver = self._parse_field(info, 'Driver name')

                    # Only include capture devices (not metadata devices)
                    if 'Video Capture' in info:
                        camera = CameraDevice(
                            path=str(device_path),
                            name=name or 'Unknown',
                            driver=driver or 'Unknown',
                            capabilities=['capture']
                        )
                        self.cameras.append(camera)
                        logger.info(f"Found camera: {camera.name} at {camera.path}")

            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout querying {device_path}")
            except FileNotFoundError:
                logger.warning("v4l2-ctl not found - install v4l-utils")
                break
            except Exception as e:
                logger.debug(f"Could not query {device_path}: {e}")

        if not self.cameras:
            logger.warning("No USB cameras detected")

        return self.cameras

    def _parse_field(self, info: str, field: str) -> Optional[str]:
        """Parse a field from v4l2-ctl output."""
        for line in info.splitlines():
            if field in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    return parts[1].strip()
        return None

    def start_recording(self, camera_path: Optional[str] = None) -> bool:
        """Start recording from a camera to a file."""
        if self.active_recording:
            logger.warning("Recording already in progress")
            return False

        # Use first camera if not specified
        if camera_path is None:
            if not self.cameras:
                self.discover_cameras()
            if not self.cameras:
                logger.error("No cameras available for recording")
                return False
            camera_path = self.cameras[0].path

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = RECORDING_DIR / f'recording_{timestamp}.{DEFAULT_FORMAT}'

        # Use ffmpeg for recording
        cmd = [
            'ffmpeg',
            '-f', 'v4l2',
            '-input_format', 'mjpeg',
            '-video_size', f'{DEFAULT_RESOLUTION[0]}x{DEFAULT_RESOLUTION[1]}',
            '-framerate', str(DEFAULT_FRAMERATE),
            '-i', camera_path,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '23',
            str(output_file)
        ]

        try:
            self.active_recording = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            logger.info(f"Started recording to {output_file}")
            return True
        except FileNotFoundError:
            logger.error("ffmpeg not found - install ffmpeg package")
            return False
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False

    def stop_recording(self) -> bool:
        """Stop the active recording."""
        if not self.active_recording:
            logger.warning("No active recording to stop")
            return False

        self.active_recording.terminate()
        try:
            self.active_recording.wait(timeout=5)
            logger.info("Recording stopped")
        except subprocess.TimeoutExpired:
            self.active_recording.kill()
            logger.warning("Recording forcefully stopped")

        self.active_recording = None
        return True

    def get_status(self) -> dict:
        """Get current camera service status."""
        return {
            'cameras_available': len(self.cameras),
            'cameras': [{'path': c.path, 'name': c.name} for c in self.cameras],
            'recording_active': self.active_recording is not None,
            'recording_dir': str(RECORDING_DIR),
        }

    def run(self):
        """Main service loop."""
        logger.info("Linnie Camera Service starting...")

        # Initial camera discovery
        self.discover_cameras()

        # Main loop - just keep service alive and rediscover periodically
        rediscover_interval = 30  # seconds
        last_discover = time.time()

        while self.running:
            current_time = time.time()

            # Periodic rediscovery for hotplug support
            if current_time - last_discover >= rediscover_interval:
                self.discover_cameras()
                last_discover = current_time

            # TODO: Add IPC mechanism for recording control
            # Options: D-Bus, Unix socket, or file-based signals

            time.sleep(1)

        # Cleanup
        if self.active_recording:
            self.stop_recording()

        logger.info("Linnie Camera Service stopped")

    def stop(self):
        """Signal the service to stop."""
        self.running = False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    camera_manager.stop()


# Global instance for signal handler
camera_manager = CameraManager()


def main():
    """Entry point for linnie-camera service."""
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        camera_manager.run()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

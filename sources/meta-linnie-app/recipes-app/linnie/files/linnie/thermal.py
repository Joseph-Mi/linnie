#!/usr/bin/env python3
"""
Linnie Thermal Monitoring Service

Monitors 6x TMP100 temperature sensors on I2C1 and provides:
- Periodic logging of all sensor readings
- Threshold alerts when temperatures exceed limits
- Sysfs-based sensor reading (uses lm75 driver)

Sensor Mapping (from thermal-overlay.dts):
    0x48: BUCK CM5
    0x49: I-BUCK CM5
    0x4A: Buck ESP32
    0x4C: BOARD
    0x4D: LDO
    0x4E: PWR INPUT
"""

import glob
import logging
import signal
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('linnie-thermal')


@dataclass
class SensorConfig:
    """Configuration for a temperature sensor."""
    name: str
    hwmon_path: Optional[Path] = None
    threshold_warn: float = 70.0   # Warning threshold in Celsius
    threshold_crit: float = 85.0   # Critical threshold in Celsius


# Sensor definitions matching the device tree
SENSORS = {
    0x48: SensorConfig(name="BUCK_CM5"),
    0x49: SensorConfig(name="I_BUCK_CM5"),
    0x4A: SensorConfig(name="BUCK_ESP32"),
    0x4C: SensorConfig(name="BOARD"),
    0x4D: SensorConfig(name="LDO"),
    0x4E: SensorConfig(name="PWR_INPUT"),
}

# Polling configuration
POLL_INTERVAL_NORMAL = 30.0    # seconds between readings (normal)
POLL_INTERVAL_ALERT = 1.0     # seconds between readings (when alert active)
LOG_INTERVAL = 60             # Log all sensors every N seconds


class ThermalMonitor:
    """Monitors TMP100 temperature sensors via sysfs."""

    def __init__(self):
        self.sensors = SENSORS.copy()
        self.running = True
        self.last_full_log = 0
        self._discover_sensors()

    def _discover_sensors(self):
        """Find hwmon paths for each sensor."""
        hwmon_base = Path('/sys/class/hwmon')

        if not hwmon_base.exists():
            logger.warning("hwmon not available - running in simulation mode")
            return

        for hwmon_dir in hwmon_base.iterdir():
            name_file = hwmon_dir / 'name'
            if name_file.exists():
                name = name_file.read_text().strip()
                # TMP100 uses lm75 driver
                if name in ('lm75', 'tmp100', 'tmp102'):
                    temp_file = hwmon_dir / 'temp1_input'
                    if temp_file.exists():
                        # Try to match to our known sensors by checking device path
                        device_path = (hwmon_dir / 'device').resolve()
                        for addr, sensor in self.sensors.items():
                            addr_hex = f'{addr:02x}'
                            if addr_hex in str(device_path):
                                sensor.hwmon_path = temp_file
                                logger.info(f"Found sensor {sensor.name} at {temp_file}")
                                break

    def read_temperature(self, sensor: SensorConfig) -> Optional[float]:
        """Read temperature from a sensor in Celsius."""
        if sensor.hwmon_path is None:
            return None

        try:
            # hwmon reports in millidegrees Celsius
            raw = int(sensor.hwmon_path.read_text().strip())
            return raw / 1000.0
        except (IOError, ValueError) as e:
            logger.error(f"Failed to read {sensor.name}: {e}")
            return None

    def check_thresholds(self, sensor: SensorConfig, temp: float) -> str:
        """Check temperature against thresholds. Returns alert level."""
        if temp >= sensor.threshold_crit:
            return 'CRITICAL'
        elif temp >= sensor.threshold_warn:
            return 'WARNING'
        return 'OK'

    def run(self):
        """Main monitoring loop."""
        logger.info("Thermal Monitor Starting...")
        logger.info(f"Monitoring {len(self.sensors)} Sensors")

        while self.running:
            current_time = time.time()
            alerts = []
            readings = {}

            # Read all sensors
            for addr, sensor in self.sensors.items():
                temp = self.read_temperature(sensor)
                if temp is not None:
                    readings[sensor.name] = temp
                    level = self.check_thresholds(sensor, temp)

                    if level == 'CRITICAL':
                        logger.critical(f"{sensor.name}: {temp:.1f}C - CRITICAL THRESHOLD EXCEEDED")
                        alerts.append(sensor.name)
                    elif level == 'WARNING':
                        logger.warning(f"{sensor.name}: {temp:.1f}C - Warning threshold exceeded")
                        alerts.append(sensor.name)

            # Periodic full log (every LOG_INTERVAL seconds)
            if current_time - self.last_full_log >= LOG_INTERVAL:
                temp_str = ', '.join(f"{name}={temp:.1f}C" for name, temp in readings.items())
                logger.info(f"Temperatures: {temp_str}")
                self.last_full_log = current_time

            # Adjust poll interval based on alert status
            interval = POLL_INTERVAL_ALERT if alerts else POLL_INTERVAL_NORMAL
            time.sleep(interval)

        logger.info("Linnie Thermal Monitor stopped")

    def stop(self):
        """Signal the monitor to stop."""
        self.running = False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    monitor.stop()


# Global monitor instance for signal handler
monitor = ThermalMonitor()


def main():
    """Entry point for linnie-thermal service."""
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        monitor.run()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

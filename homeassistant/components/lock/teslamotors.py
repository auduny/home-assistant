"""
Support for Tesla Motors locks.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/lock.teslamotors/
"""
import logging

from homeassistant.components.lock import LockDevice
from homeassistant.components.teslamotors import TeslaEntity

_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the lock."""
    if discovery_info is None:
        return
    add_devices([TeslaLock(hass, *discovery_info)])


class TeslaLock(TeslaEntity, LockDevice):
    """Represents a car lock."""

    @property
    def is_locked(self):
        """Return true if lock is locked."""
        return self.vehicle['locked']

    def lock(self, **kwargs):
        """Lock the car."""
        self.vehicle.command("door_lock")

    def unlock(self, **kwargs):
        """Unlock the car."""
        self.vehicle.command("door_unlock")

"""
Support for Tesla Motors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.TeslaMotors/

"""
import logging

from homeassistant.components.teslamotors import TeslaEntity
from homeassistant.components.binary_sensor import BinarySensorDevice

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup Tesla sensors."""
    if discovery_info is None:
        return
    add_devices([TeslaSensor(hass, *discovery_info)])


class TeslaSensor(TeslaEntity, BinarySensorDevice):
    """Representation of a Telsa sensor."""

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""

        attr = self._attribute
        if attr == "is_parked":
            if ((self.vehicle['shift_state'] == "D") or (self.vehicle['shift_state'] == "R")):
                return False
            else:
                return True
        if attr == 'is_closed':
            if (self.vehicle['ft'] or
                    self.vehicle['pr'] or
                    self.vehicle['pf'] or
                    self.vehicle['rt'] or
                    self.vehicle['df'] or
                    self.vehicle['dr']):
                return False
            else:
                return True
        val = self.vehicle[self._attribute]
        return val

    @property
    def device_class(self):
        """Return the class of this sensor, from SENSOR_CLASSES."""
        return 'moving'

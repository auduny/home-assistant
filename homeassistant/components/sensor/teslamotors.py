"""
Support for Telsa Motors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.teslamotors/

"""
import logging
import re
from homeassistant.const import LENGTH_KILOMETERS

from homeassistant.components.teslamotors import TeslaEntity, RESOURCES
_LOGGER = logging.getLogger(__name__)

MILESTOKM = 1.609344

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup Tesla sensors."""
    if discovery_info is None:
        return
    add_devices([TeslaSensor(hass, *discovery_info)])


class TeslaSensor(TeslaEntity):
    """Representation of a Tesla sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""

        attr = self._attribute
        val = self.vehicle[attr]
        if self.vehicle['is_metric']:
            if attr == 'odometer' or attr == 'ideal_battery_range':
                return round(val * MILESTOKM)  # km
            else:
                return val
        else:
            return val

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        attr = self._attribute
        if self.vehicle['is_metric']:
            if attr == 'odometer' or attr == 'ideal_battery_range':
                return LENGTH_KILOMETERS

        if attr == 'charging_state':
            return None

        return RESOURCES[self._attribute][3]

    @property
    def icon(self):
        """Return the icon."""
        return RESOURCES[self._attribute][2]

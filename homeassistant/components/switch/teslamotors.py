"""
Support for Tesla Motors Switchable stuff.

This platform uses the Telldus Live online service.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.teslamotors/
"""
import logging

from homeassistant.components.teslamotors import TeslaEntity, RESOURCES
from homeassistant.helpers.entity import ToggleEntity

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup """
    if discovery_info is None:
        return
    add_devices([TeslaSwitch(hass, *discovery_info)])


class TeslaSwitch(TeslaEntity, ToggleEntity):
    """Representation of a Tesla Model S switch."""

    @property
    def is_on(self):
        """Return true if switch is on."""
        if self._attribute == 'heater':
            return self.vehicle['is_climate_on']
        if self._attribute == 'locked':
            return self.vehicle['locked']
        if self._attribute == 'charge':
            if self.vehicle['charging_state'] == "Charging":
                return 1
            else:
                return 0

        else:
             return 0
        

    def turn_on(self, **kwargs):
        if self._attribute == 'heater':
            self.vehicle.command("auto_conditioning_start")
        if self._attribute == 'locked':
            self.vehicle.command("door_lock")
        if self._attribute == 'charge':
            self.vehicle.command("charge_start")
        else:
            _LOGGER.warning("Unknown switch")
        

    def turn_off(self, **kwargs):
        if self._attribute == 'heater':
            self.vehicle.command("auto_conditioning_stop")
        if self._attribute == 'locked':
            self.vehicle.command("door_unlock")
        if self._attribute == 'charge':
            self.vehicle.command("charge_stop")
        else:
            _LOGGER.warning("Unknown switch")


    @property
    def icon(self):
        """Return the icon."""
        return RESOURCES[self._attribute][2]

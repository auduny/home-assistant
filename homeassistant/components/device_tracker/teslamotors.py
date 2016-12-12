"""
Support for tracking a Tesla Model S or X.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/device_tracker.teslamotors/
"""
import logging

from homeassistant.util import slugify
from homeassistant.components.teslamotors import DOMAIN

_LOGGER = logging.getLogger(__name__)


def setup_scanner(hass, config, see, discovery_info=None):
    """Setup Tesla tracker."""
    if discovery_info is None:
        return

    vin, _ = discovery_info
    vehicle = hass.data[DOMAIN].vehicles[vin]

    host_name = vehicle['display_name']
    dev_id = 'tesla_' + slugify(host_name)

    def see_vehicle(vehicle):
        """Callback for reporting vehicle position."""
        see(dev_id=dev_id,
            host_name=host_name,
            gps=(vehicle['latitude'],
                 vehicle['longitude']))

    hass.data[DOMAIN].entities[vin].append(see_vehicle)
    see_vehicle(vehicle)

    return True

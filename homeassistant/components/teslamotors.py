"""
Support for Tesla Model S

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/teslamotors/
"""

from datetime import timedelta
import logging

from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD,
                                 CONF_NAME, CONF_RESOURCES)
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (TEMP_CELSIUS,LENGTH_MILES)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_point_in_utc_time
from homeassistant.util.dt import utcnow
import voluptuous as vol

DOMAIN = 'teslamotors'

REQUIREMENTS = ['teslajson==1.2.0']

_LOGGER = logging.getLogger(__name__)

CONF_UPDATE_INTERVAL = 'update_interval'
MIN_UPDATE_INTERVAL = timedelta(minutes=1)
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=1)


RESOURCES = {'position': ('device_tracker',),
             'heater': ('switch', 'Heater', 'mdi:radiator'),
             'lock': ('lock', 'Lock'),
             'charge': ('switch', 'Charge', 'mdi:battery-charging-60'),
             'odometer': ('sensor', 'Odometer', 'mdi:speedometer', LENGTH_MILES),
             'ideal_battery_range': ('sensor', 'Range', 'mdi:speedometer', LENGTH_MILES),
             'inside_temp': ('sensor', 'Inside Temp', 'mdi:thermometer', TEMP_CELSIUS),
             'outside_temp': ('sensor', 'Outside Temp', 'mdi:thermometer', TEMP_CELSIUS),
             'is_parked': ('binary_sensor', 'Parked', 'mdi:foobar'),
             'is_closed': ('binary_sensor', 'Doors Closed', 'mdi:foobar'),
             'speed': ('sensor', 'Speed', 'mdi:speedometer', 'km/h'),
             'is_climate_on': ('binary_sensor', 'Climate On', 'mdi:thermometer'),
             'charging_state': ('sensor', 'Charging', 'mdi:battery-charging-60','state'),
             'time_to_full_charge': ('sensor','Time to Full Charge', 'mdi:clock', 'hours'),
             'charge_limit_soc': ('sensor', 'Charge Limit SOC', 'mdi:battery-plus', '%'),
             'battery_level': ('sensor', 'Battery Level', 'mdi:battery-plus', '%')}

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): (
            vol.All(cv.time_period, vol.Clamp(min=MIN_UPDATE_INTERVAL))),
        vol.Optional(CONF_NAME, default={}): vol.Schema(
            {cv.slug: cv.string}),
        vol.Optional(CONF_RESOURCES): vol.All(
            cv.ensure_list, [vol.In(RESOURCES)]),
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Setup the VOC component."""
    from teslajson import Connection
    connection = Connection(
        config[DOMAIN].get(CONF_USERNAME),
        config[DOMAIN].get(CONF_PASSWORD))

    interval = config[DOMAIN].get(CONF_UPDATE_INTERVAL)

    class state:  # pylint:disable=invalid-name
        """Namespace to hold state for each vehicle."""

        entities = {}
        vehicles = {}

    hass.data[DOMAIN] = state

    def discover_vehicle(vehicle):
        """Load relevant platforms."""
        state.entities[vehicle['vin']] = []
        for attr, (component, *_) in RESOURCES.items():
            if (getattr(vehicle, attr + '_supported', True) and
                    attr in config[DOMAIN].get(CONF_RESOURCES, [attr])):
                discovery.load_platform(hass,
                                        component,
                                        DOMAIN,
                                        (vehicle['vin'], attr),
                                        config)

    def update_vehicle(vehicle):
        """Updated information on vehicle received."""
        vehicle.update(vehicle.data_request('drive_state'))
        vehicle.update(vehicle.data_request('charge_state'))
        vehicle.update(vehicle.data_request('climate_state'))
        vehicle.update(vehicle.data_request('vehicle_state'))
        vehicle['is_metric'] = hass.config.units.is_metric
        state.vehicles[vehicle['vin']] = vehicle
        if vehicle['vin'] not in state.entities:
            discover_vehicle(vehicle)
        for entity in state.entities[vehicle['vin']]:
            if isinstance(entity, Entity):
                entity.schedule_update_ha_state()
            else:
                entity(vehicle)  # device tracker
    def update(now):
        """Update status from the online service."""
        try:
            vehicles = connection.vehicles
            for vehicle in vehicles:
                update_vehicle(vehicle)
            return True
        finally:
            track_point_in_utc_time(hass, update, utcnow() + interval)

    _LOGGER.info('Logging in to service')
    return update(utcnow())


class TeslaEntity(Entity):
    """Base class for all VOC entities."""

    def __init__(self, hass, vin, attribute):
        """Initialize the entity."""
        self._hass = hass
        self._vin = vin
        self._attribute = attribute
        self._state.entities[self._vin].append(self)
        
    @property
    def _state(self):
        return self._hass.data[DOMAIN]

    @property
    def vehicle(self):
        """Return vehicle."""
        return self._state.vehicles[self._vin]

    @property
    def _vehicle_name(self):
        return (self.vehicle['display_name'])

    @property
    def _entity_name(self):
        return RESOURCES[self._attribute][1]

    @property
    def name(self):
        """Return full name of the entity."""
        return '%s %s' % (
            self._vehicle_name,
            self._entity_name)

    @property
    def should_poll(self):
        """Polling is not needed."""
        return False

    @property
    def assumed_state(self):
        """Return true if unable to access real state of entity."""
        return True

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return dict(model='%s/%s' % (
            self.vehicle['battery_level']
            self.vehicle['car_version']))

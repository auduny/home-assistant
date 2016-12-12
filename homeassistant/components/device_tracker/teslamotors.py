"""
Support for Tesla Motors 

"""
import logging
import math
from datetime import timedelta, datetime
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import track_point_in_utc_time
from homeassistant.util.dt import utcnow
from homeassistant.util import slugify
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME)
from homeassistant.components.device_tracker import (
    DEFAULT_SCAN_INTERVAL,
    PLATFORM_SCHEMA)

MIN_TIME_BETWEEN_SCANS = timedelta(minutes=1)

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['teslajson==1.0.1']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})


def setup_scanner(hass, config, see):
    """Validate the configuration and return a scanner."""
    from teslajson import Connection
    try:
        connection = Connection(
            config.get(CONF_USERNAME),
            config.get(CONF_PASSWORD))
    except Exception as err:
        _LOGGER.error("Tesla Connect failed: " + str(err))
        return
    _LOGGER.error
    interval = max(MIN_TIME_BETWEEN_SCANS,
                   config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    def _see_vehicle(vehicle):
        kmmulti = 1.609344
        dev_id = "tesla_" + slugify(vehicle["vin"])
        try:
            host_name = vehicle["display_name"]
            drive_state = vehicle.data_request('drive_state')
            charge_state = vehicle.data_request('charge_state')
            climate_state = vehicle.data_request('climate_state')
            vehicle_state = vehicle.data_request('vehicle_state')
        except Exception as err:
            _LOGGER.error("Tesla lookup failed: " + str(err))
            return
        if (vehicle_state["ft"] or
            vehicle_state["pr"] or
            vehicle_state["pf"] or
            vehicle_state["rt"] or
            vehicle_state["df"] or
            vehicle_state["dr"]):
                vehicle_state["is_open"] = True
        else:
                vehicle_state["is_open"] = False
        if drive_state["shift_state"]:
            drive_state["is_parked"] = False
        else:
            drive_state["is_parked"] = True




        _LOGGER.info('Tesla location is ' + str(drive_state["latitude"]) + " " + str(drive_state["longitude"]))
        see(dev_id=dev_id,
            host_name=host_name,
            gps=(drive_state["latitude"],
                 drive_state["longitude"]),
            attributes=dict(
            gps_as_of=datetime.fromtimestamp(drive_state["gps_as_of"]),
            charging_state=charge_state["charging_state"],
            charger_power=charge_state["charger_power"],
            ideal_battery_range=math.floor(charge_state["ideal_battery_range"]*kmmulti),
            battery=charge_state["battery_level"],
            inside_temp=climate_state["inside_temp"],
            is_climate_on=climate_state["is_climate_on"],
            outside_temp=climate_state["outside_temp"],
            is_locked=vehicle_state["locked"],
            is_open=vehicle_state["is_open"],
            speed=drive_state["speed"],
            shift_state=drive_state["shift_state"],
            is_parked=drive_state["is_parked"]))

    def update(now):
        """Update status from the online service."""
        _LOGGER.info("Updating")
        for vehicle in connection.vehicles:
            _see_vehicle(vehicle)

        track_point_in_utc_time(hass, update,
                                now + interval)

    _LOGGER.info('Logging in to service')
    return update(utcnow())

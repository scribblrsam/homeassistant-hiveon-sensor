#!/usr/bin/env python3

import requests
import voluptuous
from datetime import datetime, timedelta
import urllib.error

from .const import *

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        voluptuous.Required(CONF_MINER_ADDRESS): cv.string,
        voluptuous.Optional(CONF_CURRENCY_NAME, default="usd"): cv.string,
        voluptuous.Optional(CONF_UPDATE_FREQUENCY, default=10): cv.string,
        voluptuous.Optional(CONF_NAME_OVERRIDE, default=""): cv.string
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    LOGGER.debug("Setup Hiveon Stats Sensor")

    miner_address = config.get(CONF_MINER_ADDRESS).strip().lower()
    local_currency = config.get(CONF_CURRENCY_NAME).strip().lower()
    update_frequency = timedelta(minutes=(int(config.get(CONF_UPDATE_FREQUENCY))))
    name_override = config.get(CONF_NAME_OVERRIDE).strip()

    entities = []

    try:
        entities.append(
            HiveonStatsSensor(
                miner_address, local_currency, update_frequency, name_override
            )
        )
    except urllib.error.HTTPError as error:
        LOGGER.error(error.reason)
        return False

    add_entities(entities)


class HiveonStatsSensor(Entity):
    def __init__(self, miner_address, local_currency, update_frequency, name_override):
        self.miner_address = miner_address
        self.local_currency = local_currency
        self.update = Throttle(update_frequency)(self._update)
        if name_override:
            self._name = SENSOR_PREFIX + name_override
        else:
            self._name = SENSOR_PREFIX + miner_address
        self._icon = "mdi:ethereum"
        self._state = "Offline"
        self._active_workers = None
        self._current_hashrate = None
        self._average_hashrate_24h = None
        self._reported_hashrate = None
        self._reported_hashrate_24h = None
        self._last_update = None
        self._valid_shares = None
        self._stale_shares = None
        self._unpaid = None
        self._expected_earnings_day = None
        self._expected_earnings_week = None

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return {
            "last_update": self._last_update,
            "active_workers": self._active_workers,
            "current_hashrate": self._current_hashrate,
            "average_hashrate_24h": self._average_hashrate_24h,
            "reported_hashrate": self._reported_hashrate,
            "reported_hashrate_24h": self._reported_hashrate_24h,
            "valid_shares": self._valid_shares,
            "stale_shares": self._stale_shares
        }

    def _update(self):
        miner_stats_url = "https://hiveon.net/api/v1/stats/miner/" + self.miner_address + "/ETH"

        miner_stats_request = requests.get(url=miner_stats_url)
        miner_stats_data = miner_stats_request.json()

        if miner_stats_request.ok:
            self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
            self._active_workers = int(miner_stats_data['onlineWorkerCount'])
            if self._active_workers > 0:
                self._state = "Online"
            else:
                self._state = "Offline"
            self._current_hashrate = int(miner_stats_data['hashrate'])
            self._average_hashrate_24h = int(miner_stats_data['hashrate24h'])
            self._reported_hashrate = int(miner_stats_data['reportedHashrate'])
            self._reported_hashrate_24h = int(miner_stats_data['reportedHashrate24h'])
            self._valid_shares = int(miner_stats_data['sharesStatusStats']['validCount'])
            self._stale_shares = int(miner_stats_data['sharesStatusStats']['staleCount'])

import logging

CONF_MINER_ADDRESS = "miner_address"
CONF_UPDATE_FREQUENCY = "update_frequency"
CONF_NAME_OVERRIDE = "name_override"
CONF_CURRENCY_NAME = "local_currency"

SENSOR_PREFIX = "Hiveon Stats "

HIVEON_API_ENDPOINT = "https://hiveon.net/api/v1/stats/"
COINGECKO_API_ENDPOINT = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies="

LOGGER = logging.getLogger(__name__)

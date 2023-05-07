"""Constants for the component."""

# Component domain, used to store component data in hass data.
DOMAIN = "epex_spot"

CONF_SOURCE = "source"
CONF_MARKET_AREA = "market_area"

# possible values for CONF_SOURCE
CONF_SOURCE_AWATTAR = "Awattar"
CONF_SOURCE_EPEX_SPOT_WEB = "EPEX Spot Web Scraper"

# configuration options for net price calculation
CONF_SURCHARGE_PERC = "percentage_surcharge"
CONF_SURCHARGE_ABS = "absolute_surcharge"
CONF_VAT = "value_added_tax"

DEFAULT_SURCHARGE_PERC = 3.0
DEFAULT_SURCHARGE_ABS = 11.93
DEFAULT_VAT = 19.0


UPDATE_SENSORS_SIGNAL = f"{DOMAIN}_update_sensors_signal"

import logging
from statistics import median

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.typing import StateType

from .const import CONF_SOURCE, CONF_SOURCE_EPEX_SPOT_WEB, DOMAIN
from . import EpexSpotEntity, EpexSpotDataUpdateCoordinator as DataUpdateCoordinator

ATTR_DATA = "data"
ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up platform for a new integration.

    Called by the HA framework after async_setup_platforms has been called
    during initialization of a new integration.
    """
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = [
        EpexSpotPriceSensorEntity(coordinator),
        EpexSpotNetPriceSensorEntity(coordinator),
        EpexSpotRankSensorEntity(coordinator),
        EpexSpotQuantileSensorEntity(coordinator),
        EpexSpotLowestPriceSensorEntity(coordinator),
        EpexSpotHighestPriceSensorEntity(coordinator),
        EpexSpotAveragePriceSensorEntity(coordinator),
        EpexSpotMedianPriceSensorEntity(coordinator),
    ]

    if config_entry.data[CONF_SOURCE] == CONF_SOURCE_EPEX_SPOT_WEB:
        entities.extend(
            [
                EpexSpotBuyVolumeSensorEntity(coordinator),
                EpexSpotSellVolumeSensorEntity(coordinator),
                EpexSpotVolumeSensorEntity(coordinator),
            ]
        )

    async_add_entities(entities)


def to_ct_per_kwh(price_eur_per_mwh):
    return price_eur_per_mwh / 10


class EpexSpotPriceSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Price",
        name="Price",
        state_class=SensorStateClass.MEASUREMENT,
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)
        self._attr_icon = self._localized.icon
        self._attr_native_unit_of_measurement = self._localized.uom_per_mwh

    @property
    def native_value(self) -> StateType:
        return self._source.marketdata_now.price_eur_per_mwh

    @property
    def extra_state_attributes(self):
        data = [
            {
                ATTR_START_TIME: e.start_time.isoformat(),
                ATTR_END_TIME: e.end_time.isoformat(),
                self._localized.attr_name_per_mwh: e.price_eur_per_mwh,
                self._localized.attr_name_per_kwh: to_ct_per_kwh(e.price_eur_per_mwh),
            }
            for e in self._source.marketdata
        ]

        return {
            ATTR_DATA: data,
            self._localized.attr_name_per_kwh: to_ct_per_kwh(self.native_value),
        }


class EpexSpotNetPriceSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Net Price",
        name="Net Price",
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)
        self._attr_icon = self._localized.icon
        self._attr_native_unit_of_measurement = self._localized.uom_per_kwh

    @property
    def native_value(self) -> StateType:
        return self._source.to_net_price(self._source.marketdata_now.price_eur_per_mwh)

    @property
    def extra_state_attributes(self):
        data = [
            {
                ATTR_START_TIME: e.start_time.isoformat(),
                ATTR_END_TIME: e.end_time.isoformat(),
                self._localized.attr_name_per_kwh: self._source.to_net_price(
                    e.price_eur_per_mwh
                ),
            }
            for e in self._source.marketdata
        ]

        return {ATTR_DATA: data}


class EpexSpotBuyVolumeSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Buy Volume",
        name="Buy Volume",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement="MWh",
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)

    @property
    def native_value(self) -> StateType:
        return self._source.marketdata_now.buy_volume_mwh

    @property
    def extra_state_attributes(self):
        data = [
            {
                ATTR_START_TIME: e.start_time.isoformat(),
                ATTR_END_TIME: e.end_time.isoformat(),
                "buy_volume_mwh": e.buy_volume_mwh,
            }
            for e in self._source.marketdata
        ]

        self._attr_extra_state_attributes = {
            ATTR_DATA: data,
        }


class EpexSpotSellVolumeSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Sell Volume",
        name="Sell Volume",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement="MWh",
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)

    @property
    def native_value(self) -> StateType:
        return self._source.marketdata_now.sell_volume_mwh

    @property
    def extra_state_attributes(self):
        data = [
            {
                ATTR_START_TIME: e.start_time.isoformat(),
                ATTR_END_TIME: e.end_time.isoformat(),
                "sell_volume_mwh": e.sell_volume_mwh,
            }
            for e in self._source.marketdata
        ]

        self._attr_extra_state_attributes = {
            ATTR_DATA: data,
        }


class EpexSpotVolumeSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Volume",
        name="Volume",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement="MWh",
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)

    @property
    def native_value(self) -> StateType:
        return self._source.marketdata_now.volume_mwh

    @property
    def extra_state_attributes(self):
        data = [
            {
                ATTR_START_TIME: e.start_time.isoformat(),
                ATTR_END_TIME: e.end_time.isoformat(),
                "volume_mwh": e.volume_mwh,
            }
            for e in self._source.marketdata
        ]

        self._attr_extra_state_attributes = {
            ATTR_DATA: data,
        }


class EpexSpotRankSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Rank", name="Rank", native_unit_of_measurement=""
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)

    @property
    def native_value(self) -> StateType:
        return [
            e.price_eur_per_mwh for e in self._source.sorted_marketdata_today
        ].index(self._source.marketdata_now.price_eur_per_mwh)


class EpexSpotQuantileSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Quantile",
        name="Quantile",
        suggested_display_precision=2,
        native_unit_of_measurement="",
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)

    @property
    def native_value(self) -> StateType:
        current_price = self._source.marketdata_now.price_eur_per_mwh
        min_price = self._source.sorted_marketdata_today[0].price_eur_per_mwh
        max_price = self._source.sorted_marketdata_today[-1].price_eur_per_mwh
        return (current_price - min_price) / (max_price - min_price)


class EpexSpotLowestPriceSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Lowest Price",
        name="Lowest Price",
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)
        self._attr_icon = self._localized.icon
        self._attr_native_unit_of_measurement = self._localized.uom_per_mwh

    @property
    def native_value(self) -> StateType:
        min = self._source.sorted_marketdata_today[0]
        return min.price_eur_per_mwh

    @property
    def extra_state_attributes(self):
        min = self._source.sorted_marketdata_today[0]
        return {
            ATTR_START_TIME: min.start_time.isoformat(),
            ATTR_END_TIME: min.end_time.isoformat(),
            self._localized.attr_name_per_kwh: to_ct_per_kwh(self.native_value),
        }


class EpexSpotHighestPriceSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Highest Price",
        name="Highest Price",
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)
        self._attr_icon = self._localized.icon
        self._attr_native_unit_of_measurement = self._localized.uom_per_mwh

    @property
    def native_value(self) -> StateType:
        max = self._source.sorted_marketdata_today[-1]
        return max.price_eur_per_mwh

    @property
    def extra_state_attributes(self):
        max = self._source.sorted_marketdata_today[-1]
        return {
            ATTR_START_TIME: max.start_time.isoformat(),
            ATTR_END_TIME: max.end_time.isoformat(),
            self._localized.attr_name_per_kwh: to_ct_per_kwh(self.native_value),
        }


class EpexSpotAveragePriceSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Average Price",
        name="Average Price",
        suggested_display_precision=2,
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)
        self._attr_icon = self._localized.icon
        self._attr_native_unit_of_measurement = self._localized.uom_per_mwh

    @property
    def native_value(self) -> StateType:
        s = sum(e.price_eur_per_mwh for e in self._source.sorted_marketdata_today)
        return s / len(self._source.sorted_marketdata_today)

    @property
    def extra_state_attributes(self):
        return {
            self._localized.attr_name_per_kwh: to_ct_per_kwh(self.native_value),
        }


class EpexSpotMedianPriceSensorEntity(EpexSpotEntity, SensorEntity):
    """Home Assistant sensor containing all EPEX spot data."""

    entity_description = SensorEntityDescription(
        key="Median Price",
        name="Median Price",
        suggested_display_precision=2,
    )

    def __init__(self, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator, self.entity_description)
        self._attr_icon = self._localized.icon
        self._attr_native_unit_of_measurement = self._localized.uom_per_mwh

    @property
    def native_value(self) -> StateType:
        return median(
            [e.price_eur_per_mwh for e in self._source.sorted_marketdata_today]
        )

    @property
    def extra_state_attributes(self):
        return {
            self._localized.attr_name_per_kwh: to_ct_per_kwh(self.native_value),
        }

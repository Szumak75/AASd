# -*- coding: UTF-8 -*-
"""
Created on 6 oct 2020

@author: szumak@virthost.pl
"""
from typing import Optional

from sqlalchemy import ForeignKey, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import (
    DECIMAL,
    INTEGER,
    MEDIUMTEXT,
    SMALLINT,
    TEXT,
    TINYINT,
    VARCHAR,
)
from sqlalchemy.ext.hybrid import hybrid_property
from libs.db_models.base import LmsBase
from libs.db_models.lms.location_cities import LocationCity
from libs.db_models.lms.countries import Country
from libs.db_models.lms.location_states import LocationState
from libs.db_models.lms.location_streets import LocationStreet
from libs.db_models.lms.location_boroughs import LocationBorough
from libs.db_models.lms.location_districts import LocationDistrict


class Address(LmsBase):
    __tablename__ = "addresses"

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    id: Mapped[int] = mapped_column(
        INTEGER(11), primary_key=True, nullable=False, autoincrement=True
    )
    # `name` text COLLATE utf8_polish_ci,
    name: Mapped[str] = mapped_column(TEXT())
    # `state` varchar(64) COLLATE utf8_polish_ci DEFAULT NULL,
    state: Mapped[str] = mapped_column(VARCHAR(64), default=None)
    # `state_id` int(11) DEFAULT NULL,
    state_id: Mapped[int] = mapped_column(ForeignKey("location_states.id"))
    # `city` varchar(100) COLLATE utf8_polish_ci DEFAULT NULL,
    city: Mapped[str] = mapped_column(VARCHAR(100), default=None)
    # `city_id` int(11) DEFAULT NULL,
    city_id: Mapped[int] = mapped_column(ForeignKey("location_cities.id"))
    # `postoffice` varchar(32) COLLATE utf8_polish_ci DEFAULT NULL,
    postoffice: Mapped[str] = mapped_column(VARCHAR(32), default=None)
    # `street` varchar(255) COLLATE utf8_polish_ci DEFAULT NULL,
    street: Mapped[str] = mapped_column(VARCHAR(255), default=None)
    # `street_id` int(11) DEFAULT NULL,
    street_id: Mapped[int] = mapped_column(ForeignKey("location_streets.id"))
    # `zip` varchar(10) COLLATE utf8_polish_ci DEFAULT NULL,
    zip: Mapped[str] = mapped_column(VARCHAR(10), default=None)
    # `country_id` int(11) DEFAULT NULL,
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    # `house` varchar(20) COLLATE utf8_polish_ci DEFAULT NULL,
    house: Mapped[str] = mapped_column(VARCHAR(20), default=None)
    # `flat` varchar(20) COLLATE utf8_polish_ci DEFAULT NULL,
    flat: Mapped[str] = mapped_column(VARCHAR(20), default=None)
    # PRIMARY KEY (`id`),
    # KEY `addresses_state_id_fk` (`state_id`),
    # KEY `addresses_city_id_fk` (`city_id`),
    # KEY `addresses_street_id_fk` (`street_id`),
    # KEY `addresses_country_id_fk` (`country_id`),
    # CONSTRAINT `addresses_city_id_fk` FOREIGN KEY (`city_id`) REFERENCES `location_cities` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    location_city: Mapped["LocationCity"] = relationship("LocationCity")
    # CONSTRAINT `addresses_country_id_fk` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    location_country: Mapped["Country"] = relationship("Country")
    # CONSTRAINT `addresses_state_id_fk` FOREIGN KEY (`state_id`) REFERENCES `location_states` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    location_state: Mapped["LocationState"] = relationship("LocationState")
    # CONSTRAINT `addresses_street_id_fk` FOREIGN KEY (`street_id`) REFERENCES `location_streets` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
    location_street: Mapped["LocationStreet"] = relationship(
        "LocationStreet"
    )

    @hybrid_property
    def terc(self) -> Optional[str]:
        """Return TERC string."""
        if self.location_city:
            city: LocationCity = self.location_city
            if city.borough:
                borough: LocationBorough = city.borough
                if borough.district:
                    district: LocationDistrict = borough.district
                    if district.state:
                        state: LocationState = district.state
                        tmp = f"{state.ident}{district.ident}{borough.ident}{borough.type}"
                        if len(tmp) == 7:
                            return tmp
        return None

    @hybrid_property
    def simc(self) -> Optional[str]:
        """Return SIMC string."""
        if self.location_city:
            city: LocationCity = self.location_city
            tmp = f"{city.ident}"
            if len(tmp) == 7:
                return tmp
        return None

    @hybrid_property
    def ulic(self) -> Optional[str]:
        """Return ULIC string."""
        if self.location_street:
            street: LocationStreet = self.location_street
            tmp = f"{street.ident}"
            if len(tmp) == 5:
                return tmp
        return None

    @hybrid_property
    def nr(self) -> Optional[str]:
        """Return NR string."""
        if self.house and str(self.house).lower() != "b/n":
            return self.house
        return None

    def __repr__(self):
        return (
            f"Address(id='{self.id}', "
            f"name='{self.name}', "
            f"state='{self.state}', "
            f"state_id='{self.state_id}', "
            f"city='{self.city}', "
            f"city_id='{self.city_id}', "
            f"postoffice='{self.postoffice}', "
            f"street='{self.street}', "
            f"street_id='{self.street_id}', "
            f"zip='{self.zip}', "
            f"country_id='{self.country_id}', "
            f"house='{self.house}', "
            f"flat='{self.flat}', "
            f"location_country='{self.location_country}', "
            f"location_state='{self.location_state}', "
            f"location_city='{self.location_city}', "
            f"location_street='{self.location_street}' "
            ") "
        )

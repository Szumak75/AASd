# -*- coding: UTF-8 -*-
"""MLMS document model extension.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2020-10-06

Purpose: Extend the LMS document model for MLMS-specific usage.
"""

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

from libs.db_models.lms.documents import Document


class MDocument(Document):
    """Represent the MLMS document ORM model."""

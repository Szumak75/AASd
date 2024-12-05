# -*- coding: utf-8 -*-
"""
  connectors.py
  Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 4.12.2024, 14:00:55
  
  Purpose: Database connectors for the project.

  WWW: https://lms.org.pl/
"""

from typing import Dict, List, Optional, Any

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine import URL, engine_from_config
from sqlalchemy.util import immutabledict

from jsktoolbox.logstool.logs import LoggerClient, LoggerQueue
from jsktoolbox.attribtool import ReadOnlyClass

from libs.base.classes import BLogs, BDebug, BVerbose

import libs.db_models.mlms as mlms


class _Keys(object, metaclass=ReadOnlyClass):
    """Private Keys definition class.

    For internal purpose only.
    """

    # for database class
    DB_POOL: str = "__connection_pool__"
    SQL_DATABASE: str = "sql_database"
    SQL_PASS: str = "sql_password"
    SQL_SERVER: str = "sql_server"
    SQL_USER: str = "sql_user"


class LmsMysqlDatabase(BDebug, BVerbose, BLogs):
    """Database class."""

    def __init__(
        self,
        qlog: LoggerQueue,
        config: Dict,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Constructor."""
        self.logs = LoggerClient(queue=qlog, name=self._c_name)
        self._debug = debug
        self._verbose = verbose

        # check config
        if (
            not config
            or not isinstance(config, dict)
            or not config.get(_Keys.SQL_DATABASE)
            or not config.get(_Keys.SQL_PASS)
            or not config.get(_Keys.SQL_SERVER)
            or not config.get(_Keys.SQL_USER)
        ):
            self.logs.message_critical = "invalid config for database connector"
            return None

        # config variables
        self._set_data(
            key=_Keys.SQL_SERVER,
            value=config.get(_Keys.SQL_SERVER),
            set_default_type=List,
        )
        self._set_data(
            key=_Keys.SQL_DATABASE,
            value=config.get(_Keys.SQL_DATABASE),
            set_default_type=str,
        )
        self._set_data(
            key=_Keys.SQL_USER, value=config.get(_Keys.SQL_USER), set_default_type=str
        )
        self._set_data(
            key=_Keys.SQL_PASS, value=config.get(_Keys.SQL_PASS), set_default_type=str
        )

        # connection pool
        self._set_data(key=_Keys.DB_POOL, value=[], set_default_type=List)

    def create_connections(self) -> bool:
        """Create connection pool, second variant."""
        for dialect, fail in ("pymysql", False), ("mysqlconnector", True):
            if not fail:
                for ip in self._get_data(key=_Keys.SQL_SERVER):  # type: ignore
                    url: URL = URL.create(
                        f"mysql+{dialect}",
                        username=self._get_data(key=_Keys.SQL_USER),
                        password=self._get_data(key=_Keys.SQL_PASS),
                        host=ip,
                        database=self._get_data(key=_Keys.SQL_DATABASE),
                        port=3306,
                        query=immutabledict(
                            {
                                "charset": "utf8mb4",
                            }
                        ),
                    )
                    connection_args: Dict[str, Any] = {}
                    # connection_args["connect_timeout"] = 5
                    # create engine
                    engine: Engine = create_engine(
                        url=url,
                        connect_args=connection_args,
                        pool_recycle=3600,
                        poolclass=QueuePool,
                    )
                    try:
                        with engine.connect() as connection:
                            connection.execute(text("SELECT 1"))
                        if self.debug:
                            self.logs.message_notice = f"add connection to server: {ip} with backend: {dialect}"
                        self.__pool.append(engine)
                    except Exception as ex:
                        self.logs.message_warning = f"connect to server: {ip} with backend: {dialect} error: {ex}"
            else:
                url: URL = URL.create(
                    f"mysql+{dialect}",
                    username=self._get_data(key=_Keys.SQL_USER),
                    password=self._get_data(key=_Keys.SQL_PASS),
                    host=self._get_data(key=_Keys.SQL_SERVER)[0],  # type: ignore
                    database=self._get_data(key=_Keys.SQL_DATABASE),
                    port=3306,
                    query=immutabledict(
                        {
                            "charset": "utf8mb4",
                        }
                    ),
                )
                connection_args: Dict[str, Any] = {}
                connection_args["connect_timeout"] = 600
                connection_args["failover"] = []
                for ip in self._get_data(key=_Keys.SQL_SERVER)[1:]:  # type: ignore
                    connection_args["failover"].append(
                        {
                            "user": self._get_data(key=_Keys.SQL_USER),
                            "password": self._get_data(key=_Keys.SQL_PASS),
                            "host": ip,
                            "port": 3306,
                            "database": self._get_data(key=_Keys.SQL_DATABASE),
                            "pool_size": 5,
                            "pool_name": ip,
                        }
                    )
                # create engine
                engine: Engine = create_engine(
                    url=url,
                    connect_args=connection_args,
                    pool_recycle=3600,
                    poolclass=QueuePool,
                )
                try:
                    with engine.connect() as connection:
                        connection.execute(text("SELECT 1"))
                    if self.debug:
                        self.logs.message_notice = f"add connection to server: {self._get_data(key=_Keys.SQL_SERVER)[0]} with backend: {dialect}"  # type: ignore
                    self.__pool.append(engine)
                except Exception as ex:
                    self.logs.message_warning = f"connect to server: {self._get_data(key=_Keys.SQL_SERVER)[0]} with backend: {dialect} error: {ex}"  # type: ignore

        if self.__pool is not None and len(self.__pool) > 0:
            return True
        return False

    def create_connections_failover(self) -> bool:
        """Create connections pool.

        WARNING: incredible slow
        """
        config: Dict[str, Any] = {
            "db.url": None,
            "db.echo": False,
            "db.poolclass": QueuePool,
            "db.pool_pre_ping": True,
            "db.pool_size": 5,
            "db.max_overflow": 10,
            "db.pool_recycle": 120,
            "db.echo_pool": True,
            "db.query_cache_size": 500,
            "db.pool_timeout": 5,
            "db.pool_use_lifo": True,
        }

        for dialect, fail in ("mysqlconnector", True), ("pymysql", False):
            url = URL(
                f"mysql+{dialect}",
                username=self._get_data(key=_Keys.SQL_USER),
                password=self._get_data(key=_Keys.SQL_PASS),
                host=self._get_data(key=_Keys.SQL_SERVER)[0],  # type: ignore
                database=self._get_data(key=_Keys.SQL_DATABASE),
                port=3306,
                query=immutabledict(
                    {
                        "charset": "utf8mb4",
                    }
                ),
            )
            try:
                config["db.url"] = url
                engine: Engine

                if fail:
                    connection_args: Dict[str, Any] = {}
                    connection_args["connect_timeout"] = 600
                    # connection_args["raise_on_warnings"] = True
                    connection_args["failover"] = []
                    for ip in self._get_data(key=_Keys.SQL_SERVER)[1:]:  # type: ignore
                        connection_args["failover"].append(
                            {
                                "user": self._get_data(key=_Keys.SQL_USER),
                                "password": self._get_data(key=_Keys.SQL_PASS),
                                "host": ip,
                                "port": 3306,
                                "database": self._get_data(key=_Keys.SQL_DATABASE),
                                "pool_size": 5,
                                "pool_name": ip,
                            }
                        )

                    engine = engine_from_config(
                        config, prefix="db.", connect_args=connection_args
                    )
                else:
                    connection_args = {}
                    connection_args["connect_timeout"] = 600
                    engine = engine_from_config(
                        config, prefix="db.", connect_args=connection_args
                    )

                with engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                if self.debug:
                    self.logs.message_debug = f"add connection to server: {self._get_data(key=_Keys.SQL_SERVER)[0]} with backend: {dialect}"  # type: ignore
                self.__pool.append(engine)
                break
            except Exception as ex:
                if self.debug:
                    self.logs.message_debug = f"Create engine thrown exception: {ex}"

        if len(self.__pool) > 0:
            return True

        return False

    @property
    def session(self) -> Optional[Session]:
        """Returns db session."""
        session = None
        for item in self.__pool:
            engine: Engine = item
            try:
                session = Session(engine)
                var = session.query(func.max(mlms.MCustomer.id)).first()
                # self.logs.message_notice = f"check query: {var}"
                if self.debug:
                    self.logs.message_debug = f"create session for {engine}"

            except:
                session = None
            else:
                break

        return session

    @property
    def debug(self) -> bool:
        """Return debug flag."""
        if self._debug is not None:
            return self._debug
        return False

    @property
    def __pool(self) -> List[Engine]:
        """Returns db pool."""
        return self._get_data(key=_Keys.DB_POOL)  # type: ignore


# #[EOF]#######################################################################

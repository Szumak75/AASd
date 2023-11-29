# -*- coding: UTF-8 -*-
"""
Created on 9 oct 2020

@author: szumak
"""
# ls *.py|grep -v -E '^_' | sed -e 's/\.py//'|sed -e 's/\(.*\)/from libs.db_models.lms.\1 import */' >> __init__.py

from libs.db_models.lms.addresses import *
from libs.db_models.lms.aliasassignments import *
from libs.db_models.lms.aliases import *
from libs.db_models.lms.assignments import *
from libs.db_models.lms.cashimport import *
from libs.db_models.lms.cash import *
from libs.db_models.lms.comments import *
from libs.db_models.lms.countries import *
from libs.db_models.lms.cryptokeys import *
from libs.db_models.lms.customer_addresses import *
from libs.db_models.lms.customerassignments import *
from libs.db_models.lms.customercontacts import *
from libs.db_models.lms.customergroups import *
from libs.db_models.lms.customers import *
from libs.db_models.lms.debitnotecontents import *
from libs.db_models.lms.divisions import *
from libs.db_models.lms.docnote import *
from libs.db_models.lms.documentattachments import *
from libs.db_models.lms.documentcontents import *
from libs.db_models.lms.documents import *
from libs.db_models.lms.history_nodes import *
from libs.db_models.lms.hosts import *
from libs.db_models.lms.invoicecontents import *
from libs.db_models.lms.liabilities import *
from libs.db_models.lms.location_boroughs import *
from libs.db_models.lms.location_cities import *
from libs.db_models.lms.location_districts import *
from libs.db_models.lms.location_states import *
from libs.db_models.lms.location_streets import *
from libs.db_models.lms.location_street_types import *
from libs.db_models.lms.macs import *
from libs.db_models.lms.messageitems import *
from libs.db_models.lms.messages import *
from libs.db_models.lms.nastypes import *
from libs.db_models.lms.netdevicemodels import *
from libs.db_models.lms.netdeviceproducers import *
from libs.db_models.lms.netdevices import *
from libs.db_models.lms.netlinks import *
from libs.db_models.lms.netnodes import *
from libs.db_models.lms.netradiosectors import *
from libs.db_models.lms.networks import *
from libs.db_models.lms.nodeassignments import *
from libs.db_models.lms.nodegroupassignments import *
from libs.db_models.lms.nodegroups import *
from libs.db_models.lms.nodelocks import *
from libs.db_models.lms.nodesessions import *
from libs.db_models.lms.nodes import *
from libs.db_models.lms.numberplanassignments import *
from libs.db_models.lms.numberplans import *
from libs.db_models.lms.receiptcontents import *
from libs.db_models.lms.rtattachments import *
from libs.db_models.lms.rtcategories import *
from libs.db_models.lms.rtcategoryusers import *
from libs.db_models.lms.rtmessages import *
from libs.db_models.lms.rtqueuecategories import *
from libs.db_models.lms.rtqueues import *
from libs.db_models.lms.rtrights import *
from libs.db_models.lms.rtticketcategories import *
from libs.db_models.lms.rttickets import *
from libs.db_models.lms.tariffassignments import *
from libs.db_models.lms.tariffs import *
from libs.db_models.lms.tarifftags import *
from libs.db_models.lms.taxes import *
from libs.db_models.lms.userassignments import *
from libs.db_models.lms.usergroups import *
from libs.db_models.lms.userpanel import *
from libs.db_models.lms.users import *
from libs.db_models.lms.zipcodes import *

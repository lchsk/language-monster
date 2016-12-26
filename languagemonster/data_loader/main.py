#! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
import re

from utility.settings import Settings
from utility.utility import *
from set.maker import Maker
from sqlalchemy.orm import sessionmaker
from db.structure import *

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    s = Settings()
    s.read_parameters()
    DBSession = sessionmaker(bind=get_engine())
    session = DBSession()

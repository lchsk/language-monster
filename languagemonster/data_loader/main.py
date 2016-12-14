#! /usr/bin/python
# -*- coding: utf-8 -*-

from utility.settings import Settings
from utility.utility import *
from set.maker import Maker
from sqlalchemy.orm import sessionmaker
from db.structure import *
import re


if __name__ == '__main__':
    s = Settings()
    s.read_parameters()
    DBSession = sessionmaker(bind=get_engine())
    session = DBSession()

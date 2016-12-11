# -*- encoding: utf-8 -*-
import os
import sys
from sqlalchemy import Table, MetaData, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import sqlalchemy
from sqlalchemy.dialects import mysql
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker

from utility.utility import get_engine
from conf import languages

Base = declarative_base()

engine = get_engine()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class CategoryLinksEn(Base):
    __tablename__ = 'encategorylinks'
    # id = Column(Integer, primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint('cl_from', 'cl_to'),
    )
    cl_from = Column(Integer)
    cl_to = Column(String(255))
    cl_sortkey = Column(String(230))
    cl_timestamp = Column(DateTime)
    cl_sortkey_prefix = Column(String(255))
    cl_collation = Column(String(32))
    cl_type = Column(mysql.ENUM('page', 'subcat', 'file'))

class Category(Base):
    __tablename__ = 'category'
    __table_args = (
        PrimaryKeyConstraint('cat_id'),
    )
    cat_id = Column(Integer, primary_key=True)
    cat_title = Column(String(255))
    cat_pages = Column(Integer)
    cat_subcats = Column(Integer)
    cat_files = Column(Integer)

def rawdata(tablename):
    table_object = Table(
        tablename,
        Base.metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('word', String(200)),
        Column('desc', sqlalchemy.UnicodeText())
    )
    return table_object

def data(tablename):
    table_object = Table(
        tablename,
        Base.metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('language', String(100)),
        Column('head3', String(100)),
        Column('head4', String(100)),
        Column('word', String(100), index=True),
        Column('word_lower', String(100), index=True),
        Column('definition', sqlalchemy.UnicodeText()),
        Column('meaning', Integer),
        Column('dirty', String(1), default='F'),
        Column('comments', sqlalchemy.UnicodeText()),
        Column('popularity', Integer, default=0)
    )
    return table_object

# English

class RawDataEn(Base):
    __table__ = rawdata('en')

class DataEn(Base):
    __table__ = data('endata')

languages.t['en']['raw'] = RawDataEn
languages.t['en']['data'] = DataEn
languages.t['en']['clinks'] = CategoryLinksEn

# Polish

class RawDataPl(Base):
    __table__ = rawdata('pl')

class DataPl(Base):
    __table__ = data('pldata')

languages.t['pl']['raw'] = RawDataPl
languages.t['pl']['data'] = DataPl
languages.t['pl']['clinks'] = CategoryLinksEn

# Italian

class RawDataIt(Base):
    __table__ = rawdata('it')

class DataIt(Base):
    __table__ = data('itdata')

languages.t['it']['raw'] = RawDataIt
languages.t['it']['data'] = DataIt
languages.t['it']['clinks'] = CategoryLinksEn

# French
    
# class RawDataFr(Base):
#     __table__ = rawdata('fr')
# 
# class DataFr(Base):
#     __table__ = data('frdata')
# 
# languages.t['fr']['raw'] = RawDataFr
# languages.t['fr']['data'] = DataFr
# languages.t['fr']['clinks'] = CategoryLinksEn

# Portuguese

class RawDataPt(Base):
    __table__ = rawdata('pt')

class DataPt(Base):
    __table__ = data('ptdata')

languages.t['pt']['raw'] = RawDataPt
languages.t['pt']['data'] = DataPt
languages.t['pt']['clinks'] = CategoryLinksEn

# German

class RawDataDe(Base):
    __table__ = rawdata('de')

class DataDe(Base):
    __table__ = data('dedata')

languages.t['de']['raw'] = RawDataDe
languages.t['de']['data'] = DataDe
languages.t['de']['clinks'] = CategoryLinksEn

# Spanish

class RawDataEs(Base):
    __table__ = rawdata('es')

class DataEs(Base):
    __table__ = data('esdata')

languages.t['es']['raw'] = RawDataEs
languages.t['es']['data'] = DataEs
languages.t['es']['clinks'] = CategoryLinksEn

# French

class RawDataFr(Base):
    __table__ = rawdata('fr')

class DataFr(Base):
    __table__ = data('frdata')

languages.t['fr']['raw'] = RawDataFr
languages.t['fr']['data'] = DataFr
languages.t['fr']['clinks'] = CategoryLinksEn

######################################

def create():
    '''Creates schema'''

    print 'Creating database schema...'

    # Category.metadata.create(engine)
    Base.metadata.create_all(engine)

    print 'Database schema created.'

def get_tables(language):

    return languages.t.get(language, None)

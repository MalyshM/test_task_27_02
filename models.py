# coding: utf-8
from sqlalchemy import ARRAY, BigInteger, Column, DateTime, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class RepoActivity(Base):
    __tablename__ = 'repo_activity'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('repo_activity_id_seq'::regclass)"))
    date = Column(DateTime)
    commits = Column(Integer)
    authors = Column(ARRAY(String()))


class Repository(Base):
    __tablename__ = 'repositories'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('repositories_id_seq'::regclass)"))
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    position_cur = Column(Integer, nullable=False)
    position_prev = Column(Integer)
    stargazercount = Column(Integer, nullable=False)
    watchercount = Column(Integer, nullable=False)
    forkcount = Column(Integer, nullable=False)
    openissuescount = Column(Integer, nullable=False)
    primarylanguage = Column(String)

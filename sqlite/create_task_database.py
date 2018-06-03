from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class task_database(Base):
    """
    The class is the declarative base for the DUG task database.
    The task database is used by the task execution daemaon and the run information sync service
    Table space definition:::

    id = Column(Integer, primary_key=True) => sequential primary key autoincrementing with Insert statement

    command = Column(String(1000), nullable = False) => cmd string to be executed in the DUG tape server

    type = Column(String(10), nullable = False) => SEGD_QC, SEGY_RW or SEGY_QC

    drive = Column(String(50), nullable= False) => the dst lablel used

    sysip = Column(String(20),nullable = False) => The IP os the system submitting this

    submittime = Column(String(100), nullable = True) => Time of submission of the command to the database

    status = Column(String(10),nullable = False) => status of the job

    logpath = Column(String(500), nullable = False) => the logfile path

    exe_time =  Column(String(100), nullable = True) => The at which the execution started

    finish_time =  Column(String(100), nullable = True) => The time at which the execution finished

    exception =  Column(String(100), nullable = True) => any exceptions caught by the run info syn service
    """
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    command = Column(String(1000), nullable = False)
    type = Column(String(10), nullable = False)
    drive = Column(String(50), nullable= False)
    sysip = Column(String(20),nullable = False)
    submittime = Column(String(100), nullable = True)
    status = Column(String(10),nullable = False)
    logpath = Column(String(500), nullable = False)
    exe_time =  Column(String(100), nullable = True)
    finish_time =  Column(String(100), nullable = True)
    exception =  Column(String(100), nullable = True)



engine = create_engine('sqlite:///task_database_db.sqlite3')
Base.metadata.create_all(engine)


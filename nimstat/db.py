import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relation, relationship
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table
from sqlalchemy import Integer
from sqlalchemy import String, MetaData, Sequence
from sqlalchemy import Column
from sqlalchemy import types
from datetime import datetime
from sqlalchemy import func
import logging



metadata = MetaData()

event_type_table = Table('event_type', metadata,
    Column('id', Integer, Sequence('event_id_seq'), primary_key=True),
    Column('name', String(32), nullable=False, unique=True),
    )

user_table = Table('user', metadata,
    Column('id', Integer, Sequence('event_id_seq'), primary_key=True),
    Column('dn', String(1024), nullable=False, unique=True),
    )

create_event_table = Table('create_events', metadata,
    Column('id', Integer, Sequence('event_id_seq'), primary_key=True),
    Column('time', types.TIMESTAMP(), nullable=False),
    Column('uuid', String(64), nullable=False, unique=True),
    Column('eprkey', Integer),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('request_minutes', Integer),
    Column('charge', Integer),
    Column('cpu_count', Integer),
    Column('memory', Integer),
    Column('vmm', String(64)),
    Column('client_launch_name', String(1024)),
    Column('network', String(2048)),
    Column('event_type_id', Integer, ForeignKey('event_type.id')),
    Column('record_import_name', String(64)),
    )

remove_event_table = Table('remove_events', metadata,
    Column('id', Integer, Sequence('event_id_seq'), primary_key=True),
    Column('time', types.TIMESTAMP(), nullable=False),
    Column('uuid', String(64), nullable=False, unique=True),
    Column('eprkey', Integer),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('charge', Integer),
    Column('event_type_id', Integer, ForeignKey('event_type.id')),
    )

groups_table = Table('groups', metadata,
    Column('id', Integer, Sequence('event_id_seq'), primary_key=True),
    Column('name', String(1024), nullable=False),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    )

service_available_table = Table('service_available', metadata,
    Column('id', Integer, Sequence('service_available_id_seq'), primary_key=True),
    Column('time', types.TIMESTAMP(), nullable=False, unique=True),
    Column('test_name', String(1024), nullable=False),
    )

class EventTypeDB(object):
    def __init__(self):
        self.id = None
        self.name = None

class UserDB(object):
    def __init__(self):
        self.id = None
        self.dn = None

class CreateEventDB(object):
    def __init__(self):
        self.id = None
        self.event_type = None
        self.time = None
        self.uuid = None
        self.eprkey = None
        self.user = None
        self.request_minutes = None
        self.charge = None
        self.cpu_count = None
        self.memory = None
        self.vmm = None
        self.client_launch_name = None
        self.network = None

class RemoveEventDB(object):
    def __init__(self):
        self.id = None
        self.time = None
        self.uuid = None
        self.eprkey = None
        self.user = None
        self.charge = None
        self.event_type = None

class GroupsDB(object):
    def __init__(self):
        self.id = None
        self.name = None
        self.user = None

class ServiceAvailableDB(object):
    def __init__(self):
        pass

mapper(GroupsDB, create_event_table, properties={
    'groups': relation(EventTypeDB), 'user' : relation(UserDB)})
mapper(CreateEventDB, create_event_table, properties={
    'event_type': relation(EventTypeDB), 'user' : relation(UserDB)})
mapper(RemoveEventDB, remove_event_table, properties={
    'event_type': relation(EventTypeDB), 'user' : relation(UserDB)})
mapper(EventTypeDB, event_type_table)
mapper(UserDB, user_table)
mapper(ServiceAvailableDB, service_available_table)

class NimStatDB(object):

    def __init__(self, dburl, module=None, log=logging, default_cpu_count=1):

        self._commit_count = 0
        self._cloudconf_sections = {}
        self.default_cpu_count = default_cpu_count
        
        if module == None:
            self._engine = sqlalchemy.create_engine(dburl)
        else:
            self._engine = sqlalchemy.create_engine(dburl, module=module)
        metadata.create_all(self._engine)
        self._Session = sessionmaker(bind=self._engine)
        self._session = self._Session()

        # add the default events if not already there
        try:
            create_event = EventTypeDB()
            create_event.name = "CREATED"
            self._session.add(create_event)
            self.commit()
        except Exception, ex:
            self.rollback()

        try:
            removed_event = EventTypeDB()
            removed_event.name = "REMOVED"
            self._session.add(removed_event)
            self.commit()
        except Exception, ex:
            self.rollback()

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    def mod_commit(self):
        self._commit_count =self._commit_count + 1
        if self._commit_count == 100:
            self._commit_count = 0
            self.commit()

    def add_db_object(self, db_obj):
        self._session.add(db_obj)
        self.commit()

    def add_event(self, attrs, spinner=None):
        user_ent = self._session.query(UserDB).filter(UserDB.dn == attrs['dn']).all()
        if not user_ent:
            user_ent = UserDB()
            user_ent.dn = attrs['dn']
            self._session.add(user_ent)
            self.commit()
        else:
            user_ent = user_ent[0]  

        event_type = self._session.query(EventTypeDB).filter(EventTypeDB.name == attrs['type']).one()

        if attrs['type'] == "CREATED":
            event_ent = self._session.query(CreateEventDB).filter(CreateEventDB.uuid == attrs['uuid']).all()
            if event_ent:
                spinner.already()
                return

            event_ent = CreateEventDB()
            #  convert time Dec 16, 2010 10:59:59 AM
            event_ent.time = datetime.strptime(attrs['time'], "%b %d, %Y %I:%M:%S %p")
            event_ent.uuid = attrs['uuid']
            event_ent.eprkey = attrs['eprkey']
            event_ent.user = user_ent
            event_ent.requested_minutes = attrs['requestMinutes']
            event_ent.charge = attrs['charge']
            event_ent.cpu_count = attrs['CPUCount']
            if event_ent.cpu_count is not None and int(event_ent.cpu_count) == -1:
                event_ent.cpu_count = self.default_cpu_count
            event_ent.memory = attrs['memory']
            event_ent.vmm = attrs['vmm']
            event_ent.client_launch_name = attrs['clientLaunchName']
            event_ent.network = attrs['network']

        elif attrs['type'] == "REMOVED":
            # we could just let the db enforce this on the commit, but then we have to insert 1 at a time
            event_ent = self._session.query(RemoveEventDB).filter(RemoveEventDB.uuid == attrs['uuid']).all()
            if event_ent:
                spinner.already()
                return

            event_ent = RemoveEventDB()

            event_ent.time = datetime.strptime(attrs['time'], "%b %d, %Y %I:%M:%S %p")
            event_ent.uuid = attrs['uuid']
            event_ent.eprkey = attrs['eprkey']
            event_ent.charge = attrs['charge']
            event_ent.user = user_ent

        try:
            event_ent.event_type = event_type
            self._session.add(event_ent)
            self.commit()
            if spinner:
                spinner.next()
        except sqlalchemy.exc.IntegrityError, ex:
            self.rollback()
            if spinner:
                spinner.already()
            print ex


    def raw_sql(self, sql):
        con = self._session.connection()
        res = con.execute(sql)
        return list(res)

    def get_tests_in_period(self, start_date, end_date, test_name):
        q = self._session.query(ServiceAvailableDB).filter(ServiceAvailableDB.test_name == test_name)
        q = q.filter(ServiceAvailableDB.time >= start_date).filter(ServiceAvailableDB.time < end_date)
        return q.all()

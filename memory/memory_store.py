from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class InputLog(Base):
    __tablename__ = 'input_logs'
    id = Column(Integer, primary_key=True)
    source = Column(String)
    input_type = Column(String)
    intent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_metadata = Column(JSON)

class ExtractionLog(Base):
    __tablename__ = 'extraction_logs'
    id = Column(Integer, primary_key=True)
    agent = Column(String)
    extracted_fields = Column(JSON)
    input_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ActionLog(Base):
    __tablename__ = 'action_logs'
    id = Column(Integer, primary_key=True)
    action_type = Column(String)
    details = Column(JSON)
    input_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MemoryStore:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../flowbit_memory.sqlite')
        self.engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def log_input(self, source, input_type, intent, metadata=None):
        session = self.Session()
        log = InputLog(source=source, input_type=input_type, intent=intent, input_metadata=metadata)
        session.add(log)
        session.commit()
        input_id = log.id
        session.close()
        return input_id

    def log_extraction(self, agent, extracted_fields, input_id):
        session = self.Session()
        log = ExtractionLog(agent=agent, extracted_fields=extracted_fields, input_id=input_id)
        session.add(log)
        session.commit()
        session.close()

    def log_action(self, action_type, details, input_id):
        session = self.Session()
        log = ActionLog(action_type=action_type, details=details, input_id=input_id)
        session.add(log)
        session.commit()
        session.close()

    def get_logs(self, log_type='all'):
        session = self.Session()
        logs = {}
        if log_type in ('all', 'input'):
            logs['input'] = [l.__dict__ for l in session.query(InputLog).all()]
        if log_type in ('all', 'extraction'):
            logs['extraction'] = [l.__dict__ for l in session.query(ExtractionLog).all()]
        if log_type in ('all', 'action'):
            logs['action'] = [l.__dict__ for l in session.query(ActionLog).all()]
        session.close()
        # Remove SQLAlchemy internal state
        for k in logs:
            for entry in logs[k]:
                entry.pop('_sa_instance_state', None)
        return logs

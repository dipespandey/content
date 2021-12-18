from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

Base = declarative_base()


# class Requirement(Base):
#     __tablename__ = 'requirement'
#     id = Column(Integer, primary_key=True)
#     deadlines = Column(String)
#     languages = Column(String)
#     credits = Column(String)
#     grade = Column(String)
#     other = Column(String)
#     study_program_id = Column(Integer, ForeignKey('studyprogram.id'))
    
#     def __str__(self):
#         return f'requirements for program {self.study_program_id}'


class StudyProgram(Base):
    __tablename__ = "studyprogram"
    entry_id = Column(Integer, primary_key=True)
    coursecode = Column(String)
    title = Column(String)
    link = Column(String)
    application_link = Column(String)
    category = Column(String)
    duration = Column(String)
    credits = Column(String)
    city = Column(String)
    type = Column(String)
    description = Column(String(16000000))
    language_taught = Column(String)
    courses = Column(String(16000000))
    level = Column(String)
    deadlines = Column(String(16000000))
    languages_required = Column(String(16000000))
    grades_required = Column(String(16000000))
    others_required = Column(String(16000000))
    
    def get_requirements(self):
        return f"You have to apply by: {self.deadlines}\n \
                language: {self.languages_required}\n \
                grades: {self.grades_required}\n "
                
    def __str__(self):
        return self.coursecode


def make_tables():
    engine = create_engine("sqlite+pysqlite:///db.sqlite", echo=True, poolclass=QueuePool)
    print(engine)
    StudyProgram.__table__.create(engine)
    # Requirement.__table__.create(engine)


def create_connection():
    """Main entry point of program"""
    # Connect to the database using SQLAlchemy
    engine = create_engine("sqlite+pysqlite:///db.sqlite", echo=True, poolclass=QueuePool)
    print(engine)
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    return session
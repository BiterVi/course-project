from sqlalchemy import String, Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Rack(Base):
    __tablename__ = "shelving"

    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)
    number_cells = Column(Integer, nullable=False)
    max_weight = Column(Integer, nullable=False)


class Cargo(Base):
    __tablename__ = "cargo"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    cargo_id = Column(Integer, ForeignKey(Cargo.id, ondelete="cascade"))
    rack_id = Column(Integer, ForeignKey(Rack.id, ondelete="cascade"))
    cell_number = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)
    date = Column(String, nullable=False)

import datetime
from sqlalchemy import create_engine, Column, Integer, DateTime, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

CURRENT_SCHEMA_VERSION = 2  # 1 = initial (leads, audits), 2 = workspaces added

class SchemaVersionBase(DeclarativeBase):
    pass

class _SchemaVersion(SchemaVersionBase):
    __tablename__ = "_schema_version"
    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

def _is_sqlite(engine) -> bool:
    return "sqlite" in str(engine.url).lower()

def _get_current_version(engine) -> int:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version FROM _schema_version ORDER BY id DESC LIMIT 1"))
            row = result.fetchone()
            return row[0] if row else 0
    except Exception:
        return 0

def _set_version(engine, version: int):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        existing = session.query(_SchemaVersion).first()
        if existing:
            existing.version = version
            existing.updated_at = datetime.datetime.utcnow()
        else:
            session.add(_SchemaVersion(version=version))
        session.commit()
    finally:
        session.close()

def ensure_schema(engine, Base):
    """
    Compare le schema version attendu avec celui de la DB.
    - SQLite (local/QA) : drop + recreate automatique si obsolete.
    - PostgreSQL (prod) : raise si obsolete (migration manuelle requise).
    """
    is_sqlite = _is_sqlite(engine)
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    # Si la DB est vide (aucune table), on cree tout normalement
    if not existing_tables:
        SchemaVersionBase.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        _set_version(engine, CURRENT_SCHEMA_VERSION)
        return

    current = _get_current_version(engine)

    if current >= CURRENT_SCHEMA_VERSION:
        # Schema a jour ; on s'assure que les tables existent quand meme
        Base.metadata.create_all(bind=engine)
        return

    # Schema obsolete detecte
    if is_sqlite:
        # En local/QA : on recree proprement
        Base.metadata.drop_all(bind=engine)
        SchemaVersionBase.metadata.drop_all(bind=engine)
        SchemaVersionBase.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        _set_version(engine, CURRENT_SCHEMA_VERSION)
    else:
        raise RuntimeError(
            f"Schema version mismatch: DB is v{current}, app requires v{CURRENT_SCHEMA_VERSION}. "
            "Please run migrations before starting the app."
        )

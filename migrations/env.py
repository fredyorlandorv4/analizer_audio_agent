from __future__ import annotations
import os, sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Añade la raíz del proyecto para poder importar 'app'
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Importa settings y metadata
from app.config import settings
from app.database import Base
import app.models  # asegura que las tablas estén registradas en Base.metadata

# Config Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = settings.DATABASE_URL
    if not url:
        raise RuntimeError("DATABASE_URL no está definido")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema=None,  # o tu schema si no usas 'public'
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    url = settings.DATABASE_URL
    if not url:
        raise RuntimeError("DATABASE_URL no está definido")
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
            version_table_schema=None,  # pon tu esquema si quieres guardar ahí alembic_version
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

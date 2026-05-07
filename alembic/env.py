import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Alembic config
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use application settings so Alembic shares the same DATABASE_URL
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Import your Base and models
from app.db.base_class import Base
from app.models import *

# Metadata for autogenerate
target_metadata = Base.metadata

# Offline migrations
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# Online migrations
def run_migrations_online() -> None:
    from app.db.session import engine  # Your SQLAlchemy engine
    connectable = engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

# Determine mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
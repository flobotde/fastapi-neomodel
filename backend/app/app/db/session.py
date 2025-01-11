from neomodel import config
from neomodel.async_.core import AsyncNeo4jDriver
from app.core.config import settings
from contextlib import asynccontextmanager

# Configure neomodel async driver
config.DATABASE_URL = settings.NEO4J_BOLT_URL
config.MAX_CONNECTION_POOL_SIZE = 50
config.ENCRYPTED_CONNECTION = True
config.FORCE_TIMEZONE = True  # Ensure datetime objects have timezone info

driver = AsyncNeo4jDriver()

@asynccontextmanager
async def get_db():
    """Get an async database session context manager"""
    try:
        # Start a new session
        session = driver.session()
        yield session
    finally:
        # Ensure session is closed
        await session.close()

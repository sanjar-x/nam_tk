from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from .settings import settings

DRIVER = settings.database_driver.get_secret_value()
USER = settings.database_user.get_secret_value()
PASSWORD = settings.database_password.get_secret_value()
HOST = settings.database_host.get_secret_value()
PORT = settings.database_port.get_secret_value()
NAME = settings.database_name.get_secret_value()


engine = create_async_engine(
    url=make_url(
        name_or_url=f"{settings.database}+{DRIVER}://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"
    ),
    echo=settings.database_engine_echo,
    future=settings.database_engine_future,
    pool_size=settings.database_engine_pool_size,
    max_overflow=settings.database_engine_max_overflow,
    pool_timeout=settings.database_engine_pool_timeout,
    pool_recycle=settings.database_engine_pool_recycle,
    pool_pre_ping=settings.database_engine_pool_pre_ping,
)

async_session = async_sessionmaker(
    engine,
    autoflush=settings.database_session_autoflush,
    expire_on_commit=settings.database_session_expire_on_commit,
)

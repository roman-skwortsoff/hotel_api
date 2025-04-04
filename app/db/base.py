from pathlib import Path
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs
import environs
import os



Base = declarative_base(cls=AsyncAttrs)  # Добавляем AsyncAttrs для асинхронной работы

BASE_DIR = Path(__file__).resolve().parent.parent
env = environs.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))
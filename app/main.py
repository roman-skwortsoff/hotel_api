from fastapi import FastAPI
from app.db.session import async_engine, init_db, Base
from app.api.v1.endpoints import accommodation, service, accommodation_add, booking

app = FastAPI(title="Resort API")

@app.on_event("startup")
async def on_startup():
    """Инициализация при старте приложения"""
    await init_db()

app.include_router(accommodation_add.router)
app.include_router(accommodation.router)
app.include_router(booking.router)
app.include_router(service.router)


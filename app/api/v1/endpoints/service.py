from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_async_db, get_db
from app.models.service import Service, ServicePrice
from app.schemas.service import ServiceSchema, ServiceCreateSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.utils.enums import Weekday

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("/", response_model=list[ServiceSchema])
async def get_service(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Service).options(selectinload(Service.prices)))
    return result.scalars().all()

@router.get("/{service_id}", response_model=ServiceSchema)
async def get_service_by_id(
    service_id: int,
    db: AsyncSession = Depends(get_async_db) ):
    result = await db.execute(
        select(Service)
        .options(selectinload(Service.prices))
        .where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()

    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    return service

@router.post("/", response_model=ServiceSchema)
async def create_service(
    service_data: ServiceCreateSchema,
    db: AsyncSession = Depends(get_async_db)
):

    # Создание объекта
    new_service = Service(
        name=service_data.name,
        short_description=service_data.short_description,
        full_description=service_data.full_description,
        image=service_data.image if hasattr(service_data, 'image') else None,
        is_free=service_data.is_free,
        is_agreement_required=service_data.is_agreement_required,
    )

    # Сохранение с обработкой цен
    try:
        db.add(new_service)
        await db.flush()
        print("Записали в базу банных - ", new_service)

        if service_data.prices:
            for price in service_data.prices:
                db.add(ServicePrice(
                    service_id=new_service.id,
                    name=price.name if hasattr(price, 'name') else None,
                    weekday_type = Weekday(price.weekday_type),
                    duration_hours = price.duration_hours,
                    price=price.price,
                ))
                print( "Записываем цену: ", new_service.id)

        await db.commit()
        await db.refresh(new_service)

        return new_service

    except Exception:
        await db.rollback()
        raise

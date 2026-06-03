"""Роутер для экспорта и импорта данных."""
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_editor
from app.models.user import User
from app.services.csv_service import CsvService

router = APIRouter(prefix="/export", tags=["Экспорт / Импорт"])


@router.get("/csv", summary="Экспорт в CSV")
async def export_csv(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    Экспортирует все задачи в CSV с UTF-8 BOM.
    Исполнители в формате 'Отдел — Имя | Имя2'.
    """
    service = CsvService(db)
    content = await service.export_csv()
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=protocol.csv"},
    )


@router.get("/xlsx", summary="Экспорт в Excel")
async def export_xlsx(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Экспортирует задачи в Excel (.xlsx) с форматированием."""
    service = CsvService(db)
    content = await service.export_xlsx()
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=protocol.xlsx"},
    )


# Импорт с отдельным префиксом
import_router = APIRouter(prefix="/import", tags=["Экспорт / Импорт"])


@import_router.post("/csv", summary="Импорт из CSV")
async def import_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor),
):
    """
    Импортирует задачи из CSV.
    Исполнители сопоставляются по имени; при отсутствии — создаются новые.
    """
    service = CsvService(db)
    return await service.import_csv(file)

"""Роутер для экспорта и импорта данных."""
from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_editor
from app.models.user import User
from app.services.audit_service import log_event
from app.services.csv_service import CsvService

router = APIRouter(prefix="/export", tags=["Экспорт / Импорт"])


@router.get("/csv", summary="Экспорт в CSV")
async def export_csv(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    """
    Экспортирует все задачи в CSV с UTF-8 BOM.
    Исполнители в формате 'Отдел — Имя | Имя2'.
    """
    service = CsvService(db)
    content = await service.export_csv()
    await log_event(db, "export_csv", request=request, username=user.username)
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=protocol.csv"},
    )


@router.get("/xlsx", summary="Экспорт в Excel")
async def export_xlsx(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    """Экспортирует задачи в Excel (.xlsx) с форматированием."""
    service = CsvService(db)
    content = await service.export_xlsx()
    await log_event(db, "export_xlsx", request=request, username=user.username)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=protocol.xlsx"},
    )


# Импорт с отдельным префиксом
import_router = APIRouter(prefix="/import", tags=["Экспорт / Импорт"])


@import_router.post("/csv", summary="Импорт из CSV")
async def import_csv(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_editor),
) -> dict[str, int]:
    """
    Импортирует задачи из CSV.
    Исполнители сопоставляются по имени; при отсутствии — создаются новые.
    """
    service = CsvService(db)
    result = await service.import_csv(file)
    await log_event(
        db, "import_csv", request=request, username=user.username,
        payload={"imported": result.get("imported")},
    )
    return result

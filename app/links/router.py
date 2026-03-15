from fastapi import APIRouter, Depends

from app.auth.db import User
from app.auth.users import current_active_user
from app.config import REDIS_HOST
from app.database import get_async_session
from app.links.repository import LinkRepository
from app.links.schemas import LinkCreate, LinkUpdate, LinkStats, LinkCreateUnauthorized
from app.links.service import LinkService

router = APIRouter(prefix="/links")

import redis

redis_client = redis.from_url(REDIS_HOST)


@router.post("/shorten")
async def shorten_link(
        data: LinkCreate,
        user: User = Depends(current_active_user),
        db=Depends(get_async_session)

):
    repo = LinkRepository(db)
    service = LinkService(repo, redis_client)
    link = await service.create_link(data, user.id)

    return {
        "short_url": f"{link.short_code}"
    }


@router.get("/{short_code}")
async def redirect(
        short_code: str,
        user: User = Depends(current_active_user),
        db=Depends(get_async_session)
):
    repo = LinkRepository(db)

    service = LinkService(repo, redis_client)

    url = await service.redirect(short_code, user.id)

    return {
        "Original link": f"{url}"
    }


@router.put("/{short_code}")
async def update_link(
        short_code: str,
        data: LinkUpdate,
        db=Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    repo = LinkRepository(db)
    service = LinkService(repo, redis_client)
    await service.update(short_code, data, user.id)

    return {"status": "updated"}


@router.delete("/{short_code}")
async def delete_link(
        short_code: str,
        db=Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    repo = LinkRepository(db)

    await repo.delete(short_code, user.id)

    redis_client.delete(short_code)

    return {"status": "deleted"}


@router.get("/{short_code}/stats", response_model=LinkStats)
async def get_stats(
        short_code: str,
        db=Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    repo = LinkRepository(db)
    service = LinkService(repo, redis_client)

    result = await service.get_link(short_code, user.id)

    return result


@router.get("/search/")
async def search_link(
        original_url: str,
        db=Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    repo = LinkRepository(db)
    service = LinkService(repo, redis_client)
    links = await service.get_all_links_by_url(original_url, user.id)

    return links

# Дополнительный метод получения всех истёкших ссылок

@router.get("/expired/")
async def search_link(
        db=Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    repo = LinkRepository(db)
    service = LinkService(repo, redis_client)
    links = await service.get_all_expired_links(user.id)

    return links


#Сделал методы для получения сокращенных ссылок для незарегистрированных пользователей

@router.post("/unauthorized/shorten")
async def shorten_link_unauthorized(
        data: LinkCreateUnauthorized
):
    service = LinkService(None, redis_client)
    short_code = await service.create_unauthorized_link(data.original_url)
    return {
        "short_url": f"{short_code}"
    }


@router.get("/unauthorized/{short_code}")
async def redirect_unauthorized(
        short_code: str
):
    service = LinkService(None, redis_client)

    url = await service.redirect_unauthorized(short_code)

    return {
        "Original link": f"{url}"
    }

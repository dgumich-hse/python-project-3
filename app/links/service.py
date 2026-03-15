import pickle
import random
import string
from datetime import datetime, timezone

from fastapi import HTTPException

from app.links.models import Link

alphabet = string.ascii_letters + string.digits


def generate_code(length: int = 6):
    return "".join(random.choice(alphabet) for _ in range(length))


class LinkService:

    def __init__(self, repo, redis):

        self.repo = repo
        self.redis = redis

    async def create_link(self, data, user_id):

        code = data.custom_alias or generate_code()

        link =  await self.repo.get_by_code(code)

        if link:
            raise HTTPException(404, "Alias already exists")

        link = Link(
            short_code=code,
            original_url=data.original_url,
            expires_at=data.expires_at,
            user_id=user_id,
            custom_alias=data.custom_alias
        )

        return await self.repo.create(link)

    async def redirect(self, code, user_id):

        cached = self.redis.get(code)

        if cached:
            link = pickle.loads(cached)
            if link.user_id != user_id:
                raise HTTPException(403, "Link from another user")
        else:
            link = await self.get_link(code, user_id)

        if link.expires_at and link.expires_at < datetime.now(timezone.utc):
            raise HTTPException(404, "Link expired")

        link.clicks_count += 1
        link.last_used_at = datetime.now(timezone.utc)

        await self.repo.session.commit()
        self.redis.set(code, pickle.dumps(link), ex=3600)
        return link.original_url

    async def update(self, short_code, data, user_id):
        link = await self.repo.get_by_code(short_code)

        if link.user_id != user_id:
            raise HTTPException(403, "Link from another user")

        if not link:
            raise HTTPException(404)

        if data.expires_at:
            link.expires_at = data.expires_at

        if data.original_url:
            link.original_url = data.original_url

        await self.repo.save()
        self.redis.delete(short_code)

    async def get_link(self, short_code, user_id):
        link = await self.repo.get_by_code(short_code)

        if link.user_id != user_id:
            raise HTTPException(403, "Link from another user")

        if not link:
            raise HTTPException(404)

        return link

    async def get_all_links_by_url(self, original_url, user_id):

        links = await self.repo.find_all_by_url(original_url, user_id)

        return links.scalars().all()

    async def get_all_expired_links(self, user_id):

        links = await self.repo.find_all_expired(user_id)

        return links.scalars().all()

    # Храним ссылку от неавторизованных пользователей 10 минут и только в хеше
    async def create_unauthorized_link(self, original_url):

        code = generate_code(6)

        self.redis.set(code, original_url.encode(), ex=600)

        return code

    async def redirect_unauthorized(self, code):

        cached = self.redis.get(code)

        if cached:
            return cached.decode()

        raise HTTPException(404, "There is no such link in DB")

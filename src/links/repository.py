from datetime import datetime, timezone

from sqlalchemy import select, delete

from src.links.models import Link


class LinkRepository:

    def __init__(self, session):
        self.session = session

    async def get_by_code(self, code: str):
        query = select(Link).where(Link.short_code == code)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def create(self, link: Link):
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)

        return link

    async def delete(self, code, user_id):
        await self.session.execute(
            delete(Link).where(Link.short_code == code).where(Link.user_id == user_id)
        )

        await self.session.commit()

    async def save(self):
        await self.session.flush()
        await self.session.commit()

    async def find_all_by_url(self, original_url, user_id):
        result = await self.session.execute(
            select(Link).where(Link.original_url == original_url).where(Link.user_id == user_id)
        )

        return result

    async def find_all_expired(self, user_id):
        result = await self.session.execute(
            select(Link).where(Link.expires_at < datetime.now(timezone.utc)).where(Link.user_id == user_id)
        )

        return result

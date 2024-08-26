import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.core.models.base import Role, UserRole, role_descriptions
from src.core.services.service import Service

class RoleService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Role, db_session)


    async def get_role_by_name(self, role_name: str) -> Role:
        
        role = await self.db_session.execute(
            select(Role).filter(Role.name == role_name)
        )
        role = role.scalar_one_or_none()

        return role

    async def populate_roles(self):
        roles = [
            {
                "id": str(uuid.uuid4()), 
                "name": role.value, 
                "description": role_descriptions[role]
            }
            for role in UserRole
        ]

        existing_roles = await self.get_all()
        existing_role_names = {role.name for role in existing_roles}

        for role_data in roles:
            if role_data["name"] not in existing_role_names:
                role = Role(**role_data)
                await self.create(role)

async def setup_roles(role_service: RoleService):
    await role_service.populate_roles()
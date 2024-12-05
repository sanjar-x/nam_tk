from __future__ import annotations

import uuid
from enum import Enum
from datetime import date, time, datetime
from typing import Any, BinaryIO, List, Optional, Union

from sqlalchemy import (
    INTEGER,
    Column,
    ForeignKey,
    Table,
    UniqueConstraint,
    exists,
    update,
    extract,
    and_,
    or_,
    func,
)
from sqlalchemy.dialects.postgresql import (
    BOOLEAN,
    BYTEA,
    DATE,
    ENUM,
    INET,
    TEXT,
    TIME,
    UUID,
    VARCHAR,
    TIMESTAMP,
)
from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs
from sqlalchemy.future import select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    joinedload,
    mapped_column,
    relationship,
    selectinload,
    load_only,
    aliased,
)


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True
    id: Any

    async def _setattr_instance(self, obj):
        if obj:
            for key, value in vars(obj).items():
                if key != "_sa_instance_state":
                    setattr(self, key, value)
        return obj

    async def _execute_search(
        self,
        session: AsyncSession,
        condition: Optional[Any] = None,
        options: Optional[List[Any]] = None,
    ):
        query = select(self.__class__)

        if condition is not None:
            query = query.filter(condition)

        if options is not None:
            query = query.options(*options)

        result = await session.execute(query)
        return result.scalars().all()

    async def _execute_unique_search(
        self,
        session: AsyncSession,
        condition: Optional[Any] = None,
        options: Optional[List[Any]] = None,
    ):
        query = select(self.__class__)

        if options is not None:
            query = query.options(*options)

        if condition is not None:
            query = query.filter(condition)

        result = await session.execute(query)

        return result.unique().scalars().all()

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

    async def exist(self, session: AsyncSession, condition) -> bool | None:
        result = await session.execute(select(exists(self.__class__).where(condition)))
        return result.scalar()

    async def search(self, session: AsyncSession, filter: Any):
        return await self._execute_search(session, condition=filter)

    async def search_with_options(
        self, session: AsyncSession, options: Any, condition: Any
    ):
        return await self._execute_search(
            session, condition=condition, options=[options]
        )

    async def search_with_multi_filters(
        self, session: AsyncSession, filters: List[Any]
    ):
        condition = or_(*filters)
        return await self._execute_search(session, condition=condition)

    async def search_with_multi_options(
        self, session: AsyncSession, options: List[Any], filter: Any
    ):
        return await self._execute_search(session, condition=filter, options=options)

    async def search_with_options_and_multi_filters(
        self, session: AsyncSession, options: Any, filters: List[Any]
    ):
        condition = or_(*filters)
        return await self._execute_search(
            session, condition=condition, options=[options]
        )

    async def search_with_multi_options_and_multi_filters(
        self, session: AsyncSession, options: List[Any], filters: List[Any]
    ):
        condition = or_(*filters)
        return await self._execute_unique_search(
            session, condition=condition, options=options
        )

    async def get(self, session: AsyncSession):
        obj = await session.get(self.__class__, self.id)
        await self._setattr_instance(obj)
        return obj

    async def get_with_filter(self, session: AsyncSession, filter):
        result = await session.execute(select(self.__class__).filter(filter))
        obj = result.scalar_one_or_none()
        return await self._setattr_instance(obj)

    async def get_with_filter_with_options(
        self, session: AsyncSession, filter, options
    ):
        result = await session.execute(
            select(self.__class__).filter(filter).options(options)
        )
        obj = result.scalar_one_or_none()
        return await self._setattr_instance(obj)

    async def get_with_filter_with_multi_options(
        self, session: AsyncSession, filter, options
    ):
        result = await session.execute(
            select(self.__class__).filter(filter).options(options)
        )
        obj = result.scalar_one_or_none()
        return await self._setattr_instance(obj)

    async def get_where(self, session: AsyncSession, condition):
        result = await session.execute(select(self.__class__).where(condition))
        obj = result.scalar_one_or_none()
        return await self._setattr_instance(obj)

    async def get_where_with_options(self, session: AsyncSession, condition, options):
        result = await session.execute(
            select(self.__class__).where(condition).options(options)
        )
        obj = result.scalar_one_or_none()
        return await self._setattr_instance(obj)

    async def get_where_with_multi_options(
        self, session: AsyncSession, condition, options: List[Any]
    ):
        result = await session.execute(
            select(self.__class__).options(*options).filter(condition)
        )
        obj = result.scalar_one_or_none()
        await self._setattr_instance(obj)
        return obj

    async def get_all(self, session: AsyncSession):
        result = await session.execute(select(self.__class__))
        return result.scalars().all()

    async def get_all_where(self, session: AsyncSession, condition):
        result = await session.execute(select(self.__class__).where(condition))
        return list(result.scalars().all())

    async def get_all_where_with_options(
        self, session: AsyncSession, condition, options: List[Any]
    ):
        result = await session.execute(
            select(self.__class__).where(condition).options(*options)
        )
        return list(result.scalars().all())

    async def get_all_where_with_multi_options(
        self, session: AsyncSession, condition, options: List[Any]
    ):
        result = await session.execute(
            select(self.__class__).where(condition).options(*options)
        )
        return list(result.scalars().all())

    async def get_all_with_options(self, session: AsyncSession, options):
        result = await session.execute(select(self.__class__).options(options))
        return list(result.scalars().all())

    async def get_all_with_multi_options(
        self, session: AsyncSession, options: List[Any]
    ):
        stmt = select(self.__class__).options(*options)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def _update(self, session: AsyncSession, **kwargs):
        result = await session.execute(
            update(self.__class__).where(self.__class__.id == self.id).values(**kwargs)
        )
        await session.commit()
        return result

    async def _delete(self, session: AsyncSession) -> bool:
        instance = await session.get(self.__class__, self.id)
        if not instance:
            return False
        await session.delete(instance)
        await session.commit()
        return True

    async def delete_all(self, session: AsyncSession) -> bool:
        await session.delete(self.__class__)
        await session.commit()
        return True


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization: Mapped[str] = mapped_column(VARCHAR(255))
    full_name: Mapped[str] = mapped_column(VARCHAR(255))
    pini: Mapped[str] = mapped_column(VARCHAR(14))
    passport_series: Mapped[str] = mapped_column(VARCHAR(9))
    birth_date: Mapped[date] = mapped_column(DATE, nullable=False)
    registration_address: Mapped[str] = mapped_column(VARCHAR(255))
    work_address: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
    examination_date: Mapped[date] = mapped_column(DATE, nullable=True)

    a_type: Mapped[bool] = mapped_column(BOOLEAN, default=None, nullable=True)
    b_type: Mapped[bool] = mapped_column(BOOLEAN, default=None, nullable=True)
    c_type: Mapped[bool] = mapped_column(BOOLEAN, default=None, nullable=True)
    d_type: Mapped[bool] = mapped_column(BOOLEAN, default=None, nullable=True)
    e_type: Mapped[bool] = mapped_column(BOOLEAN, default=None, nullable=True)
    tram_type: Mapped[bool] = mapped_column(BOOLEAN, default=None, nullable=True)
    trolleybus_type: Mapped[bool] = mapped_column(BOOLEAN, default=None, nullable=True)
    hired_type: Mapped[bool] = mapped_column(BOOLEAN, default=None, nullable=True)
    special_note: Mapped[str] = mapped_column(VARCHAR(255), default=None, nullable=True)
    valid_date: Mapped[date] = mapped_column(DATE, nullable=True)
    commission_director: Mapped[str] = mapped_column(VARCHAR(255))
    finish: Mapped[bool] = mapped_column(BOOLEAN, default=False)

    async def get_by_pini(self, session: AsyncSession):
        return await self.get_where(session, self.__class__.pini == self.pini)

    async def exist_pini(self, session: AsyncSession):
        return await self.exist(session, self.__class__.pini == self.pini)

    async def search_by_query(self, session: AsyncSession, query: str):
        filters = [
            self.__class__.full_name.ilike(f"%{query}%"),
            self.__class__.pini.ilike(f"%{query}%"),
            self.__class__.passport_series.ilike(f"%{query}%"),
        ]
        return await self.search_with_multi_filters(session, filters)


# class Image(Base):
#     __tablename__ = "image"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
#     )
#     file: Mapped[bytes] = mapped_column(BYTEA)
#     file_name: Mapped[str] = mapped_column(VARCHAR(63))
#     file_path: Mapped[str] = mapped_column(TEXT)


# class Manager(User):
#     __tablename__ = "managers"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
#     )
#     role_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), ForeignKey("roles.id")
#     )

#     role: Mapped[Role] = relationship("Role", back_populates="managers")
#     department: Mapped[Department] = relationship(
#         "Department",
#         back_populates="manager",
#     )
#     __mapper_args__ = {
#         "polymorphic_identity": "manager",
#     }

#     async def search_by(self, session: AsyncSession, query: str):
#         filters = [
#             self.__class__.pini.ilike(f"%{query}%"),
#             self.__class__.first_name.ilike(f"%{query}%"),
#             self.__class__.last_name.ilike(f"%{query}%"),
#             self.__class__.phone_number.ilike(f"%{query}%"),
#             self.__class__.address.ilike(f"%{query}%"),
#         ]
#         options = [
#             joinedload(self.__class__.image),
#             joinedload(self.__class__.role)
#             .selectinload(self.__class__.role.property.mapper.class_.permissions)
#             .joinedload(
#                 self.__class__.role.property.mapper.class_.permissions.property.mapper.class_.resource
#             ),
#         ]
#         return await self.search_with_multi_options_and_multi_filters(
#             session, options, filters
#         )

#     async def get_all_with_role(self, session: AsyncSession):
#         return await self.get_all_with_options(session, joinedload(self.__class__.role))

#     async def get_all_with_role_with_permissions(self, session: AsyncSession):
#         return await self.get_all_with_options(
#             session,
#             joinedload(self.__class__.role).selectinload(
#                 self.__class__.role.property.mapper.class_.permissions
#             ),
#         )

#     async def get_all_with_role_with_permissions_with_resource(
#         self, session: AsyncSession
#     ):
#         return await self.get_all_with_options(
#             session,
#             joinedload(self.__class__.role)
#             .selectinload(self.__class__.role.property.mapper.class_.permissions)
#             .joinedload(
#                 self.__class__.role.property.mapper.class_.permissions.property.mapper.class_.resource
#             ),
#         )

#     async def get_all_with_image_and_role_with_permissions_with_resource(
#         self, session: AsyncSession
#     ):
#         options = [
#             joinedload(self.__class__.image),
#             joinedload(self.__class__.role)
#             .selectinload(self.__class__.role.property.mapper.class_.permissions)
#             .joinedload(
#                 self.__class__.role.property.mapper.class_.permissions.property.mapper.class_.resource
#             ),
#         ]
#         return await self.get_all_with_multi_options(session, options)

#     async def get_with_role_with_permissions_with_resource(self, session: AsyncSession):
#         return await self.get_where_with_options(
#             session,
#             self.__class__.id == self.id,
#             joinedload(self.__class__.role)
#             .selectinload(self.__class__.role.property.mapper.class_.permissions)
#             .joinedload(
#                 self.__class__.role.property.mapper.class_.permissions.property.mapper.class_.resource
#             ),
#         )

#     async def get_with_image_and_role_with_permissions_with_resource(
#         self, session: AsyncSession
#     ):
#         options = [
#             joinedload(self.__class__.image),
#             joinedload(self.__class__.role)
#             .selectinload(self.__class__.role.property.mapper.class_.permissions)
#             .joinedload(
#                 self.__class__.role.property.mapper.class_.permissions.property.mapper.class_.resource
#             ),
#         ]
#         await self.get_where_with_multi_options(
#             session, self.__class__.id == self.id, options
#         )

#         return self


# class Department(Base):
#     __tablename__ = "departments"
#     # Keys
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("managers.id", ondelete="SET NULL"),
#         nullable=True,
#     )
#     name: Mapped[str] = mapped_column(VARCHAR(255))
#     manager: Mapped[Optional[Manager]] = relationship(
#         "Manager", back_populates="department"
#     )
#     groups: Mapped[List[Group]] = relationship("Group", back_populates="department")

#     async def exist_name(self, session: AsyncSession):
#         return await self.exists(session, self.__class__.name == self.name)

#     async def get_all_with_manager(self, session: AsyncSession):
#         return await self.get_all_with_options(
#             session, joinedload(self.__class__.manager)
#         )

#     async def get_with_manager(self, session: AsyncSession):
#         return await self.get_where_with_options(
#             session,
#             self.__class__.id == self.id,
#             joinedload(self.__class__.manager),
#         )


# class Teacher(User):
#     __tablename__ = "teachers"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
#     )
#     specialization: Mapped[str] = mapped_column(TEXT)
#     pairs: Mapped[List[Pair]] = relationship("Pair", back_populates="teacher")
#     __mapper_args__ = {
#         "polymorphic_identity": "teacher",
#     }

#     async def search_by(self, session: AsyncSession, query: str):
#         filters = [
#             self.__class__.pini.ilike(f"%{query}%"),
#             self.__class__.first_name.ilike(f"%{query}%"),
#             self.__class__.last_name.ilike(f"%{query}%"),
#             self.__class__.phone_number.ilike(f"%{query}%"),
#             self.__class__.address.ilike(f"%{query}%"),
#             self.__class__.specialization.ilike(f"%{query}%"),
#         ]
#         return await self.search_with_options_and_multi_filters(
#             session, joinedload(self.__class__.image), filters
#         )

#     async def get_active_pair(self, session: AsyncSession):

#         current_datetime = datetime.now()
#         current_time = current_datetime.time()
#         current_date = current_datetime.date()
#         statement = (
#             select(self.__class__)
#             .options(
#                 joinedload(self.__class__.pairs).joinedload(Pair.slot),
#                 joinedload(self.__class__.pairs).joinedload(Pair.date),
#                 joinedload(self.__class__.pairs)
#                 .joinedload(Pair.groups)
#                 .joinedload(Group.students),
#                 joinedload(self.__class__.pairs)
#                 .joinedload(Pair.room)
#                 .joinedload(Room.cameras),
#             )
#             .filter(
#                 Date.date == current_date,
#                 Slot.start_time <= current_time,
#                 current_time <= Slot.end_time,
#             )
#         )

#         result = await session.execute(statement)
#         return result.scalar_one_or_none()


# groups_pairs_association = Table(
#     "groups_pairs",
#     Base.metadata,
#     Column(
#         "group_id", UUID(as_uuid=True), ForeignKey("groups.id", ondelete="SET NULL")
#     ),
#     Column("pair_id", UUID(as_uuid=True), ForeignKey("pairs.id", ondelete="SET NULL")),
# )


# class GroupType(str, Enum):
#     day = "day"
#     night = "night"
#     part = "part"


# class Group(Base):
#     __tablename__ = "groups"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     department_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("departments.id", ondelete="SET NULL"),
#         nullable=True,
#     )
#     tutor_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#     )
#     name: Mapped[str] = mapped_column(VARCHAR(255))
#     type: Mapped[Enum] = mapped_column(ENUM(GroupType), nullable=False)

#     department: Mapped[Department] = relationship("Department", back_populates="groups")
#     tutor: Mapped[Union[Manager, Teacher]] = relationship(
#         "User", back_populates="groups"
#     )

#     students: Mapped[List[Student]] = relationship(
#         "Student", back_populates="group", foreign_keys="[Student.group_id]"
#     )
#     pairs: Mapped[List[Pair]] = relationship(
#         "Pair", secondary=groups_pairs_association, back_populates="groups"
#     )

#     async def exist_name(self, session: AsyncSession):
#         return await self.exists(session, self.__class__.name == self.name)

#     async def search_by(self, session: AsyncSession, query: str):
#         options = [
#             joinedload(self.__class__.department),
#             joinedload(self.__class__.tutor).joinedload(
#                 self.__class__.tutor.property.mapper.class_.image
#             ),
#             selectinload(self.__class__.students).joinedload(
#                 self.__class__.students.property.mapper.class_.image
#             ),
#         ]
#         filters = [
#             self.__class__.name.ilike(f"%{query}%"),
#             self.__class__.tutor.property.mapper.class_.first_name.ilike(f"%{query}%"),
#             self.__class__.tutor.property.mapper.class_.last_name.ilike(f"%{query}%"),
#             self.__class__.tutor.property.mapper.class_.phone_number.ilike(
#                 f"%{query}%"
#             ),
#         ]
#         return await self.search_with_multi_options_and_multi_filters(
#             session, options, filters
#         )

#     async def get_all_with_department_and_tutor_and_students(
#         self, session: AsyncSession
#     ):
#         options = [
#             joinedload(self.__class__.department),
#             joinedload(self.__class__.tutor).joinedload(
#                 self.__class__.tutor.property.mapper.class_.image
#             ),
#             selectinload(self.__class__.students).joinedload(
#                 self.__class__.students.property.mapper.class_.image
#             ),
#         ]
#         return await self.get_all_with_multi_options(session, options)

#     async def get_with_department_and_tutor_and_students(self, session: AsyncSession):
#         options = [
#             joinedload(self.__class__.department),  # Eagerly load Department
#             joinedload(self.__class__.tutor),  # Eagerly load Tutor (User)
#             selectinload(self.__class__.students),  # Eagerly load Students
#         ]
#         return await self.get_where_with_multi_options(
#             session, self.__class__.id == self.id, options
#         )


# class Student(User):
#     __tablename__ = "students"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
#     )
#     group_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), ForeignKey("groups.id", ondelete="SET NULL")
#     )

#     group: Mapped[Group] = relationship("Group", back_populates="students")

#     __mapper_args__ = {
#         "polymorphic_identity": "student",
#     }

#     async def search_by(self, session: AsyncSession, query: str):
#         options = [joinedload(self.__class__.image), joinedload(self.__class__.group)]
#         filters = [
#             self.__class__.pini.ilike(f"%{query}%"),
#             self.__class__.first_name.ilike(f"%{query}%"),
#             self.__class__.last_name.ilike(f"%{query}%"),
#             self.__class__.phone_number.ilike(f"%{query}%"),
#             self.__class__.address.ilike(f"%{query}%"),
#             self.__class__.group.property.mapper.class_.name.ilike(f"%{query}%"),
#         ]

#         return await self.search_with_multi_options_and_multi_filters(
#             session, options, filters
#         )

#     async def get_all_with_image_and_group(self, session: AsyncSession):
#         options = [
#             joinedload(self.__class__.image),
#             joinedload(self.__class__.group),
#         ]
#         return await self.get_all_with_multi_options(session, options)


# class Subject(Base):
#     __tablename__ = "subjects"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     name: Mapped[str] = mapped_column(VARCHAR(255))

#     pairs: Mapped[List[Pair]] = relationship("Pair", back_populates="subject")

#     async def exist_name(self, session: AsyncSession):
#         return await self.exists(session, self.__class__.name == self.name)

#     async def search_by(self, session: AsyncSession, query: str):
#         return await self.search(
#             session,
#             self.__class__.name.ilike(f"%{query}%"),
#         )


# class Room(Base):
#     __tablename__ = "rooms"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     name: Mapped[str] = mapped_column(VARCHAR(255))
#     cameras: Mapped[List[Camera]] = relationship(
#         "Camera", back_populates="room", cascade="all, delete-orphan"
#     )
#     pairs: Mapped[List[Pair]] = relationship(
#         "Pair", back_populates="room", cascade="all, delete-orphan"
#     )

#     async def exist_name(self, session: AsyncSession):
#         return await self.exists(session, self.__class__.name == self.name)

#     async def search_by(self, session: AsyncSession, query: str):
#         filters = [
#             self.__class__.name.ilike(f"%{query}%"),
#             self.__class__.cameras.ip.ilike(f"%{query}%"),
#         ]
#         return await self.search_with_options_and_multi_filters(
#             session, selectinload(self.__class__.cameras), filters
#         )

#     async def get_all_with_cameras(self, session: AsyncSession):
#         return await self.get_all_with_options(
#             session,
#             selectinload(self.__class__.cameras),
#         )


# class Camera(Base):
#     __tablename__ = "cameras"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     room_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE")
#     )
#     ip: Mapped[str] = mapped_column(INET)
#     password: Mapped[str] = mapped_column(VARCHAR(255))
#     room: Mapped[Room] = relationship("Room", back_populates="cameras")
#     detections: Mapped[List[Detection]] = relationship(
#         "Detection", back_populates="camera", cascade="all, delete-orphan"
#     )

#     async def get_all_with_rooms(self, session: AsyncSession):
#         return await self.get_all_with_options(
#             session,
#             joinedload(self.__class__.room),
#         )


# class Slot(Base):
#     __tablename__ = "slots"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     start_time: Mapped[time] = mapped_column(TIME, nullable=False)
#     end_time: Mapped[time] = mapped_column(TIME, nullable=False)

#     async def get_active(self, session: AsyncSession):

#         current_time = datetime.now().time()

#         result = await session.execute(
#             select(Slot).where(
#                 Slot.start_time <= current_time, Slot.end_time > current_time
#             )
#         )
#         return result.scalar_one_or_none()


# class Date(Base):
#     __tablename__ = "dates"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     date: Mapped[date] = mapped_column(DATE, nullable=False)
#     pairs: Mapped[List[Pair]] = relationship("Pair", back_populates="date")

#     def __eq__(self, other):
#         if not isinstance(other, Date):
#             return False
#         return self.date == other.date

#     async def get_by_date(self, session: AsyncSession):
#         return await self.get_where(session, self.__class__.date == self.date)

#     async def get_active_date(self, session: AsyncSession):
#         active_date = datetime.now().date()
#         return await self.get_where(session, self.__class__.date == active_date)

#     async def get_by_year_and_month(
#         self,
#         session: AsyncSession,
#         group_id: uuid.UUID,
#         year: int | None = None,
#         month: int | None = None,
#     ):
#         options = [
#             selectinload(self.__class__.pairs).joinedload(
#                 self.__class__.pairs.property.mapper.class_.slot
#             ),
#             selectinload(self.__class__.pairs)
#             .joinedload(self.__class__.pairs.property.mapper.class_.room)
#             .selectinload(
#                 self.__class__.pairs.property.mapper.class_.room.property.mapper.class_.cameras
#             ),
#             selectinload(self.__class__.pairs)
#             .joinedload(self.__class__.pairs.property.mapper.class_.teacher)
#             .joinedload(
#                 self.__class__.pairs.property.mapper.class_.teacher.property.mapper.class_.image
#             ),
#             selectinload(self.__class__.pairs).joinedload(
#                 self.__class__.pairs.property.mapper.class_.subject
#             ),
#             selectinload(self.__class__.pairs)
#             .selectinload(self.__class__.pairs.property.mapper.class_.groups)
#             .selectinload(
#                 self.__class__.pairs.property.mapper.class_.groups.property.mapper.class_.students
#             ),
#         ]
#         filters = [self.__class__.pairs.property.mapper.class_.groups.any(id=group_id)]
#         if year and month:
#             filters.append(extract("YEAR", self.__class__.date) == year)
#             filters.append(extract("MONTH", self.__class__.date) == month)

#         return await self.get_all_where_with_multi_options(
#             session,
#             and_(*filters),
#             options,
#         )


# class Pair(Base):
#     __tablename__ = "pairs"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     date_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("dates.id", ondelete="SET NULL"),
#         nullable=True,
#     )
#     slot_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("slots.id", ondelete="SET NULL"),
#         nullable=True,
#     )
#     room_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("rooms.id", ondelete="SET NULL"),
#         nullable=True,
#     )

#     teacher_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("teachers.id", ondelete="SET NULL"),
#         nullable=True,
#     )
#     subject_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("subjects.id", ondelete="SET NULL"),
#         nullable=True,
#     )
#     date: Mapped[Date] = relationship("Date", back_populates="pairs")
#     slot: Mapped[Slot] = relationship("Slot")
#     room: Mapped[Room] = relationship("Room", back_populates="pairs")
#     teacher: Mapped[Teacher] = relationship("Teacher", back_populates="pairs")
#     subject: Mapped[Subject] = relationship("Subject", back_populates="pairs")
#     groups: Mapped[List[Group]] = relationship(
#         "Group", secondary=groups_pairs_association, back_populates="pairs"
#     )

#     async def add_groups(self, session: AsyncSession, groups: List[Group]):
#         for group in groups:
#             await session.execute(
#                 groups_pairs_association.insert().values(
#                     group_id=group.id, pair_id=self.id
#                 )
#             )

#     async def get_with_all(
#         self,
#         session: AsyncSession,
#     ):
#         options = [
#             joinedload(self.__class__.date),
#             joinedload(self.__class__.slot),
#             joinedload(self.__class__.room).selectinload(
#                 self.__class__.room.property.mapper.class_.cameras
#             ),
#             joinedload(self.__class__.subject),
#             selectinload(self.__class__.groups)
#             .selectinload(self.__class__.groups.property.mapper.class_.students)
#             .joinedload(
#                 self.__class__.groups.property.mapper.class_.students.property.mapper.class_.image
#             ),
#         ]
#         return await self.get_where_with_multi_options(
#             session,
#             self.__class__.id == self.id,
#             options,
#         )

#     async def get_all_by_teacher(
#         self,
#         session: AsyncSession,
#     ):
#         options = [
#             joinedload(self.__class__.date),
#             joinedload(self.__class__.slot),
#             joinedload(self.__class__.room).selectinload(
#                 self.__class__.room.property.mapper.class_.cameras
#             ),
#             joinedload(self.__class__.subject),
#             selectinload(self.__class__.groups)
#             .selectinload(self.__class__.groups.property.mapper.class_.students)
#             .joinedload(
#                 self.__class__.groups.property.mapper.class_.students.property.mapper.class_.image
#             ),
#         ]
#         return await self.get_all_where_with_multi_options(
#             session,
#             self.__class__.teacher_id == self.teacher_id,
#             options,
#         )

#     async def get_all_by_teacher_and_by_date(
#         self,
#         session: AsyncSession,
#     ):
#         options = [
#             joinedload(self.__class__.date),
#             joinedload(self.__class__.slot),
#             joinedload(self.__class__.room).selectinload(
#                 self.__class__.room.property.mapper.class_.cameras
#             ),
#             joinedload(self.__class__.subject),
#             selectinload(self.__class__.groups)
#             .selectinload(self.__class__.groups.property.mapper.class_.students)
#             .joinedload(
#                 self.__class__.groups.property.mapper.class_.students.property.mapper.class_.image
#             ),
#         ]
#         return await self.get_all_where_with_multi_options(
#             session,
#             and_(
#                 self.__class__.teacher_id == self.teacher_id,
#                 self.__class__.date_id == self.date_id,
#             ),
#             options,
#         )

#     async def get_with_groups_with_students_by_date_and_time_and_teacher(
#         self,
#         session: AsyncSession,
#     ):
#         options = [
#             selectinload(self.__class__.groups).selectinload(
#                 self.__class__.groups.property.mapper.class_.students
#             )
#         ]
#         return await self.get_where_with_multi_options(
#             session,
#             and_(
#                 self.__class__.teacher_id == self.teacher_id,
#                 self.__class__.date_id == self.date_id,
#                 self.__class__.slot_id == self.slot_id,
#             ),
#             options,
#         )

#     async def get_by_year_and_month(
#         self,
#         session: AsyncSession,
#         group_id: uuid.UUID,
#         year: int | None = None,
#         month: int | None = None,
#     ):
#         options = [
#             # joinedload(self.__class__.date),
#             joinedload(self.__class__.slot),
#             joinedload(self.__class__.room).selectinload(
#                 self.__class__.room.property.mapper.class_.cameras
#             ),
#             joinedload(self.__class__.teacher).joinedload(
#                 self.__class__.teacher.property.mapper.class_.image
#             ),
#             joinedload(self.__class__.subject),
#             selectinload(self.__class__.groups),
#         ]
#         filters = [self.__class__.groups.any(id=group_id)]
#         if year and month:
#             filters.append(extract("YEAR", self.__class__.date) == year)
#             filters.append(extract("MONTH", self.__class__.date) == month)

#         return await self.get_all_where_with_multi_options(
#             session,
#             and_(*filters),
#             options,
#         )

#     async def get_by_slot_and_date(self, session: AsyncSession):
#         options = [
#             joinedload(self.__class__.date),
#             joinedload(self.__class__.slot),
#             joinedload(self.__class__.room).selectinload(
#                 self.__class__.room.property.mapper.class_.cameras
#             ),
#             joinedload(self.__class__.teacher),
#             joinedload(self.__class__.subject),
#             selectinload(self.__class__.groups).selectinload(
#                 self.__class__.groups.property.mapper.class_.students
#             ),
#         ]
#         filters = [
#             self.__class__.slot_id == self.slot_id,
#             self.__class__.date_id == self.date_id,
#         ]
#         return await self.get_all_where_with_multi_options(
#             session,
#             and_(*filters),
#             options,
#         )

#     async def search_by_query(self, session: AsyncSession, query: str):
#         options = [
#             joinedload(self.__class__.date),
#             joinedload(self.__class__.slot),
#             joinedload(self.__class__.teacher),
#             joinedload(self.__class__.subject),
#             joinedload(self.__class__.room),
#             selectinload(self.__class__.groups),
#         ]
#         filters = [
#             self.__class__.room.property.mapper.class_.name.ilike(f"%{query}%"),
#             self.__class__.teacher.property.mapper.class_.first_name.ilike(
#                 f"%{query}%"
#             ),
#             self.__class__.teacher.property.mapper.class_.last_name.ilike(f"%{query}%"),
#             self.__class__.subject.property.mapper.class_.name.ilike(f"%{query}%"),
#             self.__class__.groups.property.mapper.class_.name.ilike(f"%{query}%"),
#         ]
#         return await self.search_with_multi_options_and_multi_filters(
#             session, options, filters
#         )

#     async def search_by_teacher_and_query(self, session: AsyncSession, query: str):
#         options = [
#             joinedload(self.__class__.date),
#             joinedload(self.__class__.slot),
#             joinedload(self.__class__.teacher),
#             joinedload(self.__class__.subject),
#             joinedload(self.__class__.room).selectinload(
#                 self.__class__.room.property.mapper.class_.cameras
#             ),
#             selectinload(self.__class__.groups)
#             .selectinload(self.__class__.groups.property.mapper.class_.students)
#             .selectinload(
#                 self.__class__.groups.property.mapper.class_.students.property.mapper.class_.image
#             )
#             .options(load_only(Image.file_path)),
#         ]

#         filters = [
#             self.__class__.teacher_id == self.teacher_id,
#             self.__class__.room.property.mapper.class_.name.ilike(f"%{query}%"),
#             self.__class__.teacher.property.mapper.class_.first_name.ilike(
#                 f"%{query}%"
#             ),
#             self.__class__.teacher.property.mapper.class_.last_name.ilike(f"%{query}%"),
#             self.__class__.subject.property.mapper.class_.name.ilike(f"%{query}%"),
#             self.__class__.groups.property.mapper.class_.name.ilike(f"%{query}%"),
#         ]
#         return await self.search_with_multi_options_and_multi_filters(
#             session, options, filters
#         )

#     async def search_by_group_and_query(
#         self, session: AsyncSession, group_id: uuid.UUID, query: str
#     ):
#         result = await session.execute(
#             select(Pair)
#             .join(groups_pairs_association)
#             .filter(
#                 groups_pairs_association.columns.group_id == group_id,
#                 self.__class__.room.property.mapper.class_.name.ilike(f"%{query}%"),
#                 self.__class__.teacher.property.mapper.class_.first_name.ilike(
#                     f"%{query}%"
#                 ),
#                 self.__class__.teacher.property.mapper.class_.last_name.ilike(
#                     f"%{query}%"
#                 ),
#                 self.__class__.subject.property.mapper.class_.name.ilike(f"%{query}%"),
#             )
#             .options(
#                 joinedload(self.__class__.date),
#                 joinedload(self.__class__.slot),
#                 joinedload(self.__class__.teacher),
#                 joinedload(self.__class__.subject),
#                 joinedload(self.__class__.room),
#                 joinedload(self.__class__.groups),
#             )
#         )
#         pairs = result.unique().scalars().all()
#         return pairs


# class Detection(Base):
#     __tablename__ = "detections"
#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     camera_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE")
#     )

#     user_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
#     )
#     time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
#     user: Mapped[User] = relationship("User", back_populates="detections")
#     camera: Mapped[Camera] = relationship("Camera", back_populates="detections")

#     __table_args__ = (
#         UniqueConstraint("camera_id", "user_id", "time", name="detections_time_key"),
#     )

#     async def exist_detection(self, session: AsyncSession) -> bool | None:
#         result = await session.execute(
#             select(
#                 exists(self.__class__).where(
#                     self.__class__.camera_id == self.camera_id,
#                     self.__class__.user_id == self.user_id,
#                     self.__class__.time == self.time,
#                 )
#             )
#         )
#         return result.scalar()

#     async def get_last(self, session: AsyncSession):
#         result = await session.execute(
#             select(func.max(self.__class__.time)).where(
#                 and_(
#                     self.__class__.camera_id == self.camera_id,
#                     self.__class__.user_id == self.user_id,
#                 )
#             )
#         )
#         return result.scalar_one_or_none()

#     async def get_users_last_detections(self, session: AsyncSession):
#         # Подзапрос для получения max(time) для каждой пары (camera_id, user_id)
#         subquery = (
#             select(
#                 self.__class__.user_id,
#                 func.max(self.__class__.time).label("max_time"),
#             )
#             .group_by(self.__class__.user_id)
#             .subquery()
#         )

#         # Создаем алиас для Detection
#         detection_alias = aliased(self.__class__)

#         # Основной запрос для получения записей с max(time)
#         query = (
#             select(detection_alias).join(
#                 subquery,
#                 and_(
#                     detection_alias.user_id == subquery.columns.user_id,
#                     detection_alias.time == subquery.columns.max_time,
#                 ),
#             )
#             # Подключаем joinedload для загрузки связанных сущностей
#             .options(
#                 joinedload(detection_alias.camera).joinedload(Camera.room),
#                 joinedload(detection_alias.user),
#             )
#         )

#         # Выполняем запрос
#         result = await session.execute(query)
#         return result.scalars().all()

#     async def get_managers_last_detections(self, session: AsyncSession):
#         # Подзапрос для получения max(time) для каждой пары (user_id)
#         subquery = (
#             select(
#                 self.__class__.user_id,
#                 func.max(self.__class__.time).label("max_time"),
#             )
#             .group_by(self.__class__.user_id)
#             .subquery()
#         )

#         # Создаем алиас для Detection
#         detection_alias = aliased(self.__class__)

#         # Создаем алиас для User
#         user_alias = aliased(User)

#         # Основной запрос для получения записей с max(time) только для пользователей типа 'student'
#         query = (
#             select(detection_alias)
#             .join(
#                 subquery,
#                 and_(
#                     detection_alias.user_id == subquery.c.user_id,
#                     detection_alias.time == subquery.c.max_time,
#                 ),
#             )
#             .join(
#                 user_alias,
#                 detection_alias.user_id == user_alias.id,
#             )
#             .where(user_alias.type == "managers")  # Фильтр по типу пользователя
#             # Подключаем joinedload для загрузки связанных сущностей
#             .options(
#                 joinedload(detection_alias.camera).joinedload(Camera.room),
#                 joinedload(detection_alias.user),
#             )
#         )
#         result = await session.execute(query)
#         return result.scalars().all()

#     async def get_teachers_last_detections(self, session: AsyncSession):
#         subquery = (
#             select(
#                 self.__class__.user_id,
#                 func.max(self.__class__.time).label("max_time"),
#             )
#             .group_by(self.__class__.user_id)
#             .subquery()
#         )

#         # Создаем алиас для Detection
#         detection_alias = aliased(self.__class__)

#         # Создаем алиас для User
#         user_alias = aliased(User)

#         # Основной запрос для получения записей с max(time) только для пользователей типа 'student'
#         query = (
#             select(detection_alias)
#             .join(
#                 subquery,
#                 and_(
#                     detection_alias.user_id == subquery.c.user_id,
#                     detection_alias.time == subquery.c.max_time,
#                 ),
#             )
#             .join(
#                 user_alias,
#                 detection_alias.user_id == user_alias.id,
#             )
#             .where(user_alias.type == "teacher")  # Фильтр по типу пользователя
#             # Подключаем joinedload для загрузки связанных сущностей
#             .options(
#                 joinedload(detection_alias.camera).joinedload(Camera.room),
#                 joinedload(detection_alias.user),
#             )
#         )
#         result = await session.execute(query)
#         return result.scalars().all()

#     async def get_students_last_detections(self, session: AsyncSession):
#         # Подзапрос для получения max(time) для каждой пары (user_id)
#         subquery = (
#             select(
#                 self.__class__.user_id,
#                 func.max(self.__class__.time).label("max_time"),
#             )
#             .group_by(self.__class__.user_id)
#             .subquery()
#         )

#         # Создаем алиас для Detection
#         detection_alias = aliased(self.__class__)

#         # Создаем алиас для User
#         user_alias = aliased(User)

#         # Основной запрос для получения записей с max(time) только для пользователей типа 'student'
#         query = (
#             select(detection_alias)
#             .join(
#                 subquery,
#                 and_(
#                     detection_alias.user_id == subquery.c.user_id,
#                     detection_alias.time == subquery.c.max_time,
#                 ),
#             )
#             .join(
#                 user_alias,
#                 detection_alias.user_id == user_alias.id,
#             )
#             .where(user_alias.type == "student")  # Фильтр по типу пользователя
#             # Подключаем joinedload для загрузки связанных сущностей
#             .options(
#                 joinedload(detection_alias.camera).joinedload(Camera.room),
#                 joinedload(detection_alias.user),
#             )
#         )

#         # Выполняем запрос
#         result = await session.execute(query)
#         return result.scalars().all()

#     async def get_users_last_detections_in_range(
#         self, session: AsyncSession, start_time: datetime, end_time: datetime
#     ):
#         # Подзапрос для получения max(time) для каждого user_id
#         subquery = (
#             select(
#                 self.__class__.user_id,
#                 func.max(self.__class__.time).label("max_time"),
#             )
#             .group_by(self.__class__.user_id)
#             # Добавляем фильтр по временному диапазону
#             .where(self.__class__.time.between(start_time, end_time))
#             .subquery()
#         )

#         # Создаем алиас для Detection
#         detection_alias = aliased(self.__class__)

#         # Основной запрос для получения записей с max(time) для каждого пользователя
#         query = (
#             select(detection_alias).join(
#                 subquery,
#                 and_(
#                     detection_alias.user_id == subquery.c.user_id,
#                     detection_alias.time == subquery.c.max_time,
#                 ),
#             )
#             # Подключаем joinedload для загрузки связанных сущностей
#             .options(
#                 joinedload(detection_alias.camera).joinedload(Camera.room),
#                 joinedload(detection_alias.user),
#             )
#         )

#         # Выполняем запрос
#         result = await session.execute(query)
#         return result.scalars().all()

#     async def get_managers_last_detections_in_range(
#         self, session: AsyncSession, start_time: datetime, end_time: datetime
#     ):
#         # Подзапрос для получения max(time) для каждого user_id
#         subquery = (
#             select(
#                 self.__class__.user_id,
#                 func.max(self.__class__.time).label("max_time"),
#             )
#             .where(
#                 self.__class__.time.between(start_time, end_time)
#             )  # Фильтр по времени
#             .group_by(self.__class__.user_id)
#             .subquery()
#         )

#         # Создаем алиас для Detection
#         detection_alias = aliased(self.__class__)

#         # Создаем алиас для User
#         user_alias = aliased(User)

#         # Основной запрос для получения записей с max(time) для студентов
#         query = (
#             select(detection_alias)
#             .join(
#                 subquery,
#                 and_(
#                     detection_alias.user_id == subquery.c.user_id,
#                     detection_alias.time == subquery.c.max_time,
#                 ),
#             )
#             .join(
#                 user_alias,
#                 detection_alias.user_id == user_alias.id,
#             )
#             .where(user_alias.type == "manager")  # Фильтр по типу пользователя
#             # Подключаем joinedload для загрузки связанных сущностей
#             .options(
#                 joinedload(detection_alias.camera).joinedload(Camera.room),
#                 joinedload(detection_alias.user),
#             )
#         )

#         # Выполняем запрос
#         result = await session.execute(query)
#         return result.scalars().all()

#     async def get_teachers_last_detections_in_range(
#         self, session: AsyncSession, start_time: datetime, end_time: datetime
#     ):
#         # Подзапрос для получения max(time) для каждого user_id
#         subquery = (
#             select(
#                 self.__class__.user_id,
#                 func.max(self.__class__.time).label("max_time"),
#             )
#             .where(
#                 self.__class__.time.between(start_time, end_time)
#             )  # Фильтр по времени
#             .group_by(self.__class__.user_id)
#             .subquery()
#         )

#         # Создаем алиас для Detection
#         detection_alias = aliased(self.__class__)

#         # Создаем алиас для User
#         user_alias = aliased(User)

#         # Основной запрос для получения записей с max(time) для студентов
#         query = (
#             select(detection_alias)
#             .join(
#                 subquery,
#                 and_(
#                     detection_alias.user_id == subquery.c.user_id,
#                     detection_alias.time == subquery.c.max_time,
#                 ),
#             )
#             .join(
#                 user_alias,
#                 detection_alias.user_id == user_alias.id,
#             )
#             .where(user_alias.type == "teacher")  # Фильтр по типу пользователя
#             # Подключаем joinedload для загрузки связанных сущностей
#             .options(
#                 joinedload(detection_alias.camera).joinedload(Camera.room),
#                 joinedload(detection_alias.user),
#             )
#         )

#         # Выполняем запрос
#         result = await session.execute(query)
#         return result.scalars().all()

#     async def get_students_last_detections_in_range(
#         self, session: AsyncSession, start_time: datetime, end_time: datetime
#     ):
#         # Подзапрос для получения max(time) для каждого user_id
#         subquery = (
#             select(
#                 self.__class__.user_id,
#                 func.max(self.__class__.time).label("max_time"),
#             )
#             .where(
#                 self.__class__.time.between(start_time, end_time)
#             )  # Фильтр по времени
#             .group_by(self.__class__.user_id)
#             .subquery()
#         )

#         # Создаем алиас для Detection
#         detection_alias = aliased(self.__class__)

#         # Создаем алиас для User
#         user_alias = aliased(User)

#         # Основной запрос для получения записей с max(time) для студентов
#         query = (
#             select(detection_alias)
#             .join(
#                 subquery,
#                 and_(
#                     detection_alias.user_id == subquery.c.user_id,
#                     detection_alias.time == subquery.c.max_time,
#                 ),
#             )
#             .join(
#                 user_alias,
#                 detection_alias.user_id == user_alias.id,
#             )
#             .where(user_alias.type == "student")  # Фильтр по типу пользователя
#             # Подключаем joinedload для загрузки связанных сущностей
#             .options(
#                 joinedload(detection_alias.camera).joinedload(Camera.room),
#                 joinedload(detection_alias.user),
#             )
#         )

#         # Выполняем запрос
#         result = await session.execute(query)
#         return result.scalars().all()

#     async def get_range(
#         self, session: AsyncSession, start_time: float, end_time: float
#     ):
#         stmt = select(self.__class__).where(
#             self.__class__.time.between(start_time, end_time)
#         )
#         result = await session.execute(stmt)
#         return result.scalars().all()

#     async def get_range_by_camera(
#         self,
#         session: AsyncSession,
#         start_time: float,
#         end_time: float,
#     ):
#         stmt = (
#             select(self.__class__)
#             .where(
#                 and_(
#                     self.__class__.time.between(start_time, end_time),
#                     self.__class__.camera_id == self.camera_id,
#                 )
#             )
#             .group_by(self.__class__.user_id)
#         )
#         result = await session.execute(stmt)
#         return result.scalars().all()

#     async def get_range_by_cameras(
#         self,
#         session: AsyncSession,
#         start_time: float,
#         end_time: float,
#         cameras: list[uuid.UUID],
#     ):
#         stmt = (
#             select(self.__class__)
#             .where(
#                 and_(
#                     self.__class__.time.between(start_time, end_time),
#                     self.__class__.camera_id.in_(cameras),
#                 )
#             )
#             .group_by(self.__class__.user_id)
#         )
#         result = await session.execute(stmt)
#         return result.scalars().all()

#     async def get_last_in_range_by_cameras(
#         self,
#         session: AsyncSession,
#         start_time: datetime,
#         end_time: datetime,
#         cameras: list[uuid.UUID],
#     ):
#         subquery = (
#             select(
#                 self.__class__.user_id,
#                 self.__class__.camera_id,
#                 func.max(self.__class__.time).label("max_time"),
#             )
#             .where(
#                 and_(
#                     self.__class__.time.between(start_time, end_time),  # Time filter
#                     self.__class__.camera_id.in_(cameras),  # Filter by multiple cameras
#                 )
#             )
#             .group_by(self.__class__.user_id, self.__class__.camera_id)
#             .subquery()
#         )

#         detection_alias = aliased(self.__class__)
#         user_alias = aliased(User)

#         # Main query to get records with max(time) for the specified cameras
#         query = (
#             select(detection_alias)
#             .join(
#                 subquery,
#                 and_(
#                     detection_alias.user_id == subquery.c.user_id,
#                     detection_alias.camera_id == subquery.c.camera_id,
#                     detection_alias.time == subquery.c.max_time,
#                 ),
#             )
#             .join(
#                 user_alias,
#                 detection_alias.user_id == user_alias.id,
#             )
#             .options(
#                 joinedload(detection_alias.camera).joinedload(Camera.room),
#                 joinedload(detection_alias.user),
#             )
#         )

#         # Execute the query
#         result = await session.execute(query)
#         return result.scalars().all()

#     async def get_range_by_user(
#         self,
#         session: AsyncSession,
#         start_time: float,
#         end_time: float,
#     ):
#         stmt = (
#             select(self.__class__)
#             .where(
#                 and_(
#                     self.__class__.time.between(start_time, end_time),
#                     self.__class__.user_id == self.user_id,
#                 )
#             )
#             .group_by(self.__class__.camera_id)
#         )
#         result = await session.execute(stmt)
#         return result.scalars().all()

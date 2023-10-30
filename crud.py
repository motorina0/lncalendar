from typing import List, Optional, Union

from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import (
    CreateSchedule,
    Schedule,
    UnavailableTime,
    CreateUnavailableTime,
    CreateAppointment,
    Appointment,
)


## Schedule CRUD
async def create_schedule(wallet_id: str, data: CreateSchedule) -> Schedule:
    schedule_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO lncalendar.schedule (id, wallet, name, start_day, end_day, start_time, end_time, amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            schedule_id,
            wallet_id,
            data.name,
            data.start_day,
            data.end_day,
            data.start_time,
            data.end_time,
            data.amount,
        ),
    )
    schedule = await get_schedule(schedule_id)
    assert schedule, "Newly created schedule couldn't be retrieved"
    return schedule


async def update_schedule(schedule_id: str, data: CreateSchedule) -> Schedule:
    await db.execute(
        """
        UPDATE lncalendar.schedule SET name = ?, start_day = ?, end_day = ?, start_time = ?, end_time = ?, amount = ?
        WHERE id = ?
        """,
        (
            data.name,
            data.start_day,
            data.end_day,
            data.start_time,
            data.end_time,
            data.amount,
            schedule_id,
        ),
    )
    schedule = await get_schedule(schedule_id)
    assert schedule, "Updated schedule couldn't be retrieved"
    return schedule


async def get_schedule(schedule_id: str) -> Optional[Schedule]:
    row = await db.fetchone(
        "SELECT * FROM lncalendar.schedule WHERE id = ?", (schedule_id,)
    )
    return Schedule(**row) if row else None


async def get_schedules(wallet_ids: Union[str, List[str]]) -> List[Schedule]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM lncalendar.schedule WHERE wallet IN ({q})", (*wallet_ids,)
    )

    return [Schedule(**row) for row in rows]


async def delete_schedule(schedule_id: str) -> None:
    await db.execute("DELETE FROM lncalendar.schedule WHERE id = ?", (schedule_id,))


## Appointment CRUD
async def create_appointment(
    schedule_id: str, payment_hash: str, data: CreateAppointment
) -> Appointment:
    appointment_id = payment_hash
    await db.execute(
        """
        INSERT INTO lncalendar.appointment (id, name, email, info, start_time, end_time, schedule)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            appointment_id,
            data.name,
            data.email,
            data.info,
            data.start_time,
            data.end_time,
            schedule_id,
        ),
    )
    appointment = await get_appointment(appointment_id)
    assert appointment, "Newly created appointment couldn't be retrieved"
    return appointment


async def get_appointment(appointment_id: str) -> Optional[Appointment]:
    row = await db.fetchone(
        "SELECT * FROM lncalendar.appointment WHERE id = ?", (appointment_id,)
    )
    return Appointment(**row) if row else None


async def get_appointments(schedule_id: str) -> List[Appointment]:
    rows = await db.fetchall(
        "SELECT * FROM lncalendar.appointment WHERE schedule = ?", (schedule_id,)
    )
    return [Appointment(**row) for row in rows]


async def get_appointments_wallets(
    wallet_ids: Union[str, List[str]]
) -> List[Appointment]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM lncalendar.appointment WHERE wallet IN ({q})", (*wallet_ids,)
    )
    return [Appointment(**row) for row in rows]


async def set_appointment_paid(appointment_id: str) -> None:
    await db.execute(
        """
        UPDATE lncalendar.appointment SET paid = true
        WHERE id = ?
        """,
        (appointment_id,),
    )
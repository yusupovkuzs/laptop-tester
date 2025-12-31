from sqlalchemy import insert, update
from app.db.connection import engine
from app.db.models import test_sessions, usb_tests, audio_tests
from datetime import datetime

def create_session(serial=None):
    with engine.begin() as conn:
        result = conn.execute(
            insert(test_sessions).values(
                laptop_serial=serial,
                started_at=datetime.utcnow()
            ).returning(test_sessions.c.id)
        )
        return result.scalar()

def finish_session(session_id, status):
    with engine.begin() as conn:
        conn.execute(
            update(test_sessions)
            .where(test_sessions.c.id == session_id)
            .values(
                finished_at=datetime.utcnow(),
                overall_status=status
            )
        )

def save_usb_test(session_id, result):
    with engine.begin() as conn:
        conn.execute(
            insert(usb_tests).values(
                session_id=session_id,
                drive=result.get("drive"),
                write_speed_mb_s=result.get("write_speed_mb_s"),
                read_speed_mb_s=result.get("read_speed_mb_s"),
                checksum_ok=result.get("checksum_match"),
                status="PASS" if result.get("status") == "OK" else "FAIL",
                error=result.get("error")
            )
        )

def save_audio_test(session_id, device, channel, ok, error=None):
    with engine.begin() as conn:
        conn.execute(
            insert(audio_tests).values(
                session_id=session_id,
                device_name=device,
                channel=channel,
                status="PASS" if ok else "FAIL",
                error=error
            )
        )

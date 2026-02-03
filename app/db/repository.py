from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete, select
from app.db.connection import SessionLocal, engine
from app.db.models import test_sessions, usb_tests, audio_tests
from app.db.models import test_sessions, usb_tests, audio_tests

# Сохранение результатов USB теста
def save_usb_test(laptop_serial,  usb_results: list[dict]):
    with engine.begin() as conn:
        # Удаляем старые тесты этого ноутбука
        conn.execute(
            delete(usb_tests).where(usb_tests.c.laptop_serial == laptop_serial)
        )

        # Добавляем новые
        for usb in usb_results:
            conn.execute(
                usb_tests.insert().values(
                    laptop_serial=laptop_serial,
                    drive=usb["drive"],
                    write_speed=usb["write_speed"],
                    read_speed=usb["read_speed"],
                    status=usb["status"],
                    error=usb["error"],
                )
            )

# Сохранение результатов аудио теста
def save_audio_test(laptop_serial, left_speakers, right_speakers, left_headphones, right_headphones, error=None):
    session = SessionLocal()
    try:
        stmt = insert(audio_tests).values(
            laptop_serial=laptop_serial,
            left_headphones=left_headphones,
            right_headphones=right_headphones,
            left_speakers=left_speakers,
            right_speakers=right_speakers,
            error=error
        ).on_conflict_do_update(
            index_elements=['laptop_serial'],
            set_={
                "left_headphones": left_headphones,
                "right_headphones": right_headphones,
                "left_speakers": left_speakers,
                "right_speakers": right_speakers,
                "error": error
            }
        )
        session.execute(stmt)
        session.commit()
    finally:
        session.close()

# Завершение сессии с итоговым результатом
def finish_test_session(laptop_serial, tester_name, overall_status):
    session = SessionLocal()
    try:
        stmt = insert(test_sessions).values(
            laptop_serial=laptop_serial,
            tester_name=tester_name,
            overall_status=overall_status
        ).on_conflict_do_update(
            index_elements=['laptop_serial'],
            set_={
                "tester_name": tester_name,
                "overall_status": overall_status
            }
        )
        session.execute(stmt)
        session.commit()
    finally:
        session.close()

def get_session_by_serial(laptop_serial):
    with SessionLocal() as db:
        session_row = db.execute(
            test_sessions.select().where(test_sessions.c.laptop_serial == laptop_serial)
        ).mappings().first()

        audio_rows = db.execute(
            audio_tests.select().where(audio_tests.c.laptop_serial == laptop_serial)
        ).fetchone()

        usb_rows = db.execute(
            usb_tests.select().where(usb_tests.c.laptop_serial == laptop_serial)
        ).mappings().all()

    return session_row, audio_rows, usb_rows

def get_all_sessions():
    with engine.connect() as conn:
        result = conn.execute(select(test_sessions)).mappings().all()
        return result




from sqlalchemy.dialects.postgresql import insert
from app.db.connection import SessionLocal, engine
from app.db.models import test_sessions, usb_tests, audio_tests
from app.db.models import metadata, test_sessions, usb_tests, audio_tests

# Сохранение результатов USB теста
def save_usb_test(laptop_serial, checksum_ok, status, error=None):
    session = SessionLocal()
    try:
        stmt = insert(usb_tests).values(
            laptop_serial=laptop_serial,
            checksum_ok=checksum_ok,
            status=status,
            error=error
        ).on_conflict_do_update(
            index_elements=['laptop_serial'],  # по какому ключу обновлять
            set_={
                "checksum_ok": checksum_ok,
                "status": status,
                "error": error
            }
        )
        session.execute(stmt)
        session.commit()
    finally:
        session.close()

# Сохранение результатов аудио теста
def save_audio_test(laptop_serial, device_name, left_status, right_status, error=None):
    session = SessionLocal()
    try:
        stmt = insert(audio_tests).values(
            laptop_serial=laptop_serial,
            device_name=device_name,
            left_status=left_status,
            right_status=right_status,
            error=error
        ).on_conflict_do_update(
            index_elements=['laptop_serial'],
            set_={
                "device_name": device_name,
                "left_status": left_status,
                "right_status": right_status,
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
    return None  # Заглушка для функции

def get_all_sessions():
    return []  # Заглушка для функции




from sqlalchemy import (
    Table, Column, Text, Integer, Boolean, MetaData,
    TIMESTAMP, CheckConstraint
)
from sqlalchemy.sql import func

metadata = MetaData()

# ------------------- Сессии -------------------
test_sessions = Table(
    "test_sessions", metadata,
    Column("laptop_serial", Text, primary_key=True),
    Column("tester_name", Text, nullable=False),
    Column("finished_at", TIMESTAMP, server_default=func.now()),
    Column("overall_status", Text, nullable=False),
    CheckConstraint("overall_status IN ('PASS','FAIL','CANCELLED')", name="check_overall_status")
)

# ------------------- USB тесты -------------------
usb_tests = Table(
    "usb_tests", metadata,
    Column("id", Integer, primary_key=True),
    Column("laptop_serial", Text, index=True),  # привязка по серийному номеру
    Column("drive", Text),                      # какой USB
    Column("write_speed", Integer),
    Column("read_speed", Integer),
    Column("status", Text, nullable=False),
    Column("error", Text),
    CheckConstraint("status IN ('PASS','FAIL')", name="check_usb_status")
)

# ------------------- Аудио тесты -------------------
audio_tests = Table(
    "audio_tests", metadata,
    Column("laptop_serial", Text, primary_key=True),  # привязка по серийному номеру
    Column("device_name", Text),
    Column("left_status", Text),
    Column("right_status", Text),
    Column("error", Text),
    CheckConstraint("left_status IN ('PASS','FAIL')", name="check_audio_left_status"),
    CheckConstraint("right_status IN ('PASS','FAIL')", name="check_audio_right_status")
)

from sqlalchemy import (
    Table, Column, Integer, Text, Boolean,
    ForeignKey, MetaData, TIMESTAMP
)

metadata = MetaData()

test_sessions = Table(
    "test_sessions", metadata,
    Column("id", Integer, primary_key=True),
    Column("laptop_serial", Text),
    Column("started_at", TIMESTAMP),
    Column("finished_at", TIMESTAMP),
    Column("overall_status", Text)
)

usb_tests = Table(
    "usb_tests", metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", Integer, ForeignKey("test_sessions.id")),
    Column("drive", Text),
    Column("write_speed_mb_s", Integer),
    Column("read_speed_mb_s", Integer),
    Column("checksum_ok", Boolean),
    Column("status", Text),
    Column("error", Text)
)

audio_tests = Table(
    "audio_tests", metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", Integer, ForeignKey("test_sessions.id")),
    Column("device_name", Text),
    Column("channel", Text),
    Column("status", Text),
    Column("error", Text)
)

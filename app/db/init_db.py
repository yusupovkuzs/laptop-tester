from app.db.connection import engine
from app.db.models import metadata

def init_db():
    metadata.create_all(engine)
    print("Таблицы успешно созданы")

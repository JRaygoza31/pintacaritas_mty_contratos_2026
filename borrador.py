from app import app
from extensiones import db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE evento
            ADD COLUMN IF NOT EXISTS tipo_fiesta VARCHAR(50);
        """))
        conn.commit()

    print("✅ Columna tipo_fiesta creada correctamente")

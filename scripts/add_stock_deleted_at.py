"""
Añade columnas/tablas faltantes en SQLite: stock.deleted_at, stock_history, item_requests.
Ejecutar desde la raíz del proyecto con el .venv activado:

  python scripts/add_stock_deleted_at.py
"""
import os
import sys
from pathlib import Path

# Raíz del proyecto y src en el path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
os.chdir(ROOT)

# Cargar solo la config para obtener la URI (sin crear la app Flask)
from dotenv import load_dotenv
load_dotenv()

INSTANCE_DIR = ROOT / 'instance'
DATABASE_URI = os.environ.get('DATABASE_URI')
if not DATABASE_URI:
    INSTANCE_DIR.mkdir(exist_ok=True)
    db_path = INSTANCE_DIR / 'mi_base_datos.db'
    DATABASE_URI = f'sqlite:///{db_path}'

def main():
    if not DATABASE_URI.startswith('sqlite'):
        print('Este script solo corrige SQLite. Para PostgreSQL usa: flask db upgrade')
        return
    path = DATABASE_URI.replace('sqlite:///', '')
    if not Path(path).is_file():
        print(f'No existe la base de datos: {path}')
        return
    import sqlite3
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    # 1) Columna deleted_at en stock
    cur.execute("SELECT 1 FROM pragma_table_info('stock') WHERE name='deleted_at'")
    if not cur.fetchone():
        cur.execute('ALTER TABLE stock ADD COLUMN deleted_at DATETIME')
        print('Columna stock.deleted_at añadida.')

    # 2) Tabla stock_history si no existe
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_history'")
    if not cur.fetchone():
        cur.execute("""
            CREATE TABLE stock_history (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER NOT NULL,
                changed_by INTEGER NOT NULL,
                action VARCHAR(20) NOT NULL,
                old_value TEXT,
                new_value TEXT,
                timestamp DATETIME,
                FOREIGN KEY(stock_id) REFERENCES stock (id) ON DELETE CASCADE,
                FOREIGN KEY(changed_by) REFERENCES users (id)
            )
        """)
        cur.execute('CREATE INDEX idx_stock_history_stock ON stock_history (stock_id)')
        cur.execute('CREATE INDEX idx_stock_history_date ON stock_history (timestamp)')
        print('Tabla stock_history creada.')

    # 3) Tabla item_requests (solicitudes de elementos)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='item_requests'")
    if not cur.fetchone():
        cur.execute("""
            CREATE TABLE item_requests (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stock_id INTEGER,
                request_username VARCHAR(80),
                request_date DATE NOT NULL,
                duration_type VARCHAR(20) NOT NULL,
                duration_value INTEGER,
                signed BOOLEAN NOT NULL DEFAULT 0,
                signed_at DATETIME,
                status VARCHAR(20) NOT NULL DEFAULT 'pendiente',
                delivery_date DATE,
                created_at DATETIME NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY(stock_id) REFERENCES stock (id) ON DELETE SET NULL
            )
        """)
        cur.execute('CREATE INDEX idx_item_request_user ON item_requests (user_id)')
        cur.execute('CREATE INDEX idx_item_request_date ON item_requests (request_date)')
        print('Tabla item_requests creada.')
    else:
        # Añadir columnas nuevas si faltan
        for col, typ in [('stock_id', 'INTEGER'), ('status', "VARCHAR(20) DEFAULT 'pendiente'"), ('delivery_date', 'DATE')]:
            cur.execute(f"SELECT 1 FROM pragma_table_info('item_requests') WHERE name=?", (col,))
            if not cur.fetchone():
                cur.execute(f'ALTER TABLE item_requests ADD COLUMN {col} {typ}')
                print(f'Columna item_requests.{col} añadida.')

    conn.commit()
    conn.close()
    print('Listo. Vuelve a intentar crear el stock.')

if __name__ == '__main__':
    main()

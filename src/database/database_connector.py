import sqlite3
import logging
from src.config import Config

class DatabaseConnector:
    def __init__(self, db_path=Config.DATABASE_URL):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)


    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        # Habilitar WAL para mejorar la concurrencia
        conn.execute('PRAGMA journal_mode=WAL;')
        return conn

    
    def initialize_database(self):
        conn = self.get_conn()
        cursor = conn.cursor()


        # Crear tabla de configuraciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                id TEXT PRIMARY KEY,
                entity_id INTEGER NOT NULL,       
                sync_interval_minutes INTEGER,
                parking_hours_allowed INTEGER,
                visit_size_limit INTEGER,
                parking_size_limit INTEGER,
                last_sync DATETIME DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
        ''')


        # Crear tabla de vehículos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                user_type TEXT NOT NULL,
                plate TEXT NOT NULL UNIQUE,
                vehicle_type TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Crear tabla de estacionamientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                identifier TEXT NOT NULL UNIQUE,
                current_license_plate TEXT,
                is_for_visit BOOLEAN NOT NULL,
                available BOOLEAN NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expiration_date DATETIME,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_sync BOOLEAN DEFAULT FALSE
            )
        ''')

        # Crear tabla de eventos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                poc_id INTEGER NOT NULL,
                plate TEXT NOT NULL,
                type TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                sync BOOLEAN DEFAULT FALSE
            )
        ''')

        # Crear índices para optimizar búsquedas
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicles_plate ON vehicles (plate)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_parking_identifier ON parking (identifier)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_synced ON events (plate)')

        conn.commit()
        conn.close()
        self.logger.info("Database created")



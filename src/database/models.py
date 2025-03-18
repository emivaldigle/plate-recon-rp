import logging
from datetime import datetime, timezone, timedelta
from src.database.database_connector import DatabaseConnector

# Configuración básica de logging
logging.basicConfig(level=logging.DEBUG)

class VehicleModel:
    
    def __init__(self):
        self.db = DatabaseConnector()
    
    def find_vehicle_by_plate(self, plate):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE plate = ?", (plate,))
        vehicle = cursor.fetchone()
        conn.close()
        logging.debug(f"Vehicle found by plate {plate}: {vehicle}")
        return vehicle
    
    def find_last_sync_vehicle(self):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles ORDER BY updated_at DESC LIMIT 1")
        vehicle = cursor.fetchone()
        conn.close()
        logging.debug(f"Last synced vehicle: {vehicle}")
        return vehicle

    def create_vehicle(self, vehicle_data):
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vehicles (id, plate, vehicle_type, user_id, user_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', vehicle_data)
            conn.commit()  # Confirma la transacción
            logging.debug(f"Vehicle inserted with data: {vehicle_data}")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error inserting vehicle: {e}")
        finally:
            conn.close()

    def update_vehicle(self, vehicle_data):
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE vehicles SET plate = ?, vehicle_type = ?, user_id = ?, user_type = ?, created_at = ?, updated_at = ?
                WHERE id = ?
            ''', vehicle_data)
            conn.commit()  # Confirma la transacción
            logging.debug(f"Vehicle updated with data: {vehicle_data}")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error updating vehicle: {e}")
        finally:
            conn.close()

class ConfigModel:
    def __init__(self):
        self.db = DatabaseConnector()

    def find_config(self, entity_id):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM config WHERE entity_id = ?", (entity_id,))
        config = cursor.fetchone()
        conn.close()
        logging.debug(f"Config found for entity_id {entity_id}: {config}")
        return config
    
    def init_config(self, config_data):
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO config (entity_id, sync_interval_minutes, parking_hours_allowed, visit_size_limit, parking_size_limit, last_sync, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', config_data)
            conn.commit()  # Confirma la transacción
            logging.debug(f"Config inserted with data: {config_data}")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error inserting configuration: {e}")
        finally:
            conn.close()

    def update_config(self, config_data, entity_id):
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE config 
                SET sync_interval_minutes = ?, 
                    parking_hours_allowed = ?, 
                    visit_size_limit = ?, 
                    parking_size_limit = ?, 
                    last_sync = ?,
                    active = ?
                WHERE entity_id = ?
            ''', config_data + (entity_id,)) 
            conn.commit()  # Confirma la transacción
            logging.debug(f"Config updated for entity_id {entity_id} with data: {config_data}")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error updating configuration: {e}")
        finally:
            conn.close()

class ParkingModel:
    def __init__(self):
        self.db = DatabaseConnector()

    def find_last_sync_parking(self):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parking ORDER BY updated_at DESC LIMIT 1")
        parking = cursor.fetchone()
        conn.close()
        logging.debug(f"Last synced parking: {parking}")
        return parking
    
    def find_by_user_id(self, user_id):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parking WHERE user_id = ? AND available = 1", (user_id,))
        parking = cursor.fetchone()
        conn.close()
        logging.debug(f"Parking found by identifier {user_id}: {parking}")
        return parking
    
    def find_parking_by_identifier(self, identifier):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parking WHERE identifier = ?", (identifier,))
        parking = cursor.fetchone()
        conn.close()
        logging.debug(f"Parking found by identifier {identifier}: {parking}")
        return parking

    def update_parking_availability(self, identifier, available, plate, last_updated):
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE parking
                SET available = ?,
                current_license_plate = ?,
                updated_at = ?
                WHERE identifier = ?
            ''', (available, plate, last_updated, identifier))
            conn.commit()  # Confirma la transacción
            logging.debug(f"Parking availability updated for identifier {identifier} to available: {available}")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error updating parking availability {e}")
        finally:
            conn.close()

    def update_parking_sync(self, identifier):
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE parking
                SET is_sync = 1
                WHERE identifier = ?
            ''', (identifier,))
            conn.commit()  # Confirma la transacción
            logging.debug(f"Parking sync status updated for identifier {identifier}")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error updating parking sync {e}")
        finally:
            conn.close()

    def create_parking(self, parking_data):
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO parking (id, user_id, identifier, current_license_plate, is_for_visit, available, created_at, expiration_date, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', parking_data)
            conn.commit()  # Confirma la transacción
            logging.debug(f"Parking inserted with data: {parking_data}")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error inserting parking: {e}")
        finally:
            conn.close()

    def update_parking(self, parking_data):
        last_sync = datetime.now()

        parking_data_with_sync = parking_data + (last_sync,)  
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE parking SET user_id = ?, 
                           identifier = ?, 
                           current_license_plate = ?, 
                           is_for_visit = ?, 
                           available = ?, 
                           created_at = ?, 
                           expiration_date = ?,
                           updated_at = ?
                WHERE id = ?
            ''', parking_data_with_sync)
            conn.commit()  # Confirma la transacción
            logging.debug(f"Parking updated with data: {parking_data_with_sync}")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error updating parking: {e}")
        finally:
            conn.close()

class EventModel:
    def __init__(self):
        self.db = DatabaseConnector()

    def mark_event_as_synced(self, event_id):
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE events
                SET sync = TRUE
                WHERE id = ?           
            ''', (event_id,))
            conn.commit()  # Confirma la transacción
            logging.debug(f"Event with id {event_id} synced successfully")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error marking event as sync: {e}")
        finally:
            conn.close()

    def register_event(self, event_id, event_type, poc_id, plate):
        conn = self.db.get_conn()
        try:
            conn.execute('BEGIN TRANSACTION')  # Inicia la transacción
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (id, type, poc_id, plate, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_id, event_type, poc_id, plate, datetime.now()))
            conn.commit()  # Confirma la transacción
            logging.debug(f"Event registered with type {event_type} and plate {plate}")
        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            logging.error(f"Error registering event: {e}")
        finally:
            conn.close()
        
    def find_last_event_by_plate(self, plate):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE plate = ? ORDER BY created_at DESC", (plate,))
        event = cursor.fetchone()
        conn.close()
        logging.debug(f"Event found by plate {plate}: {event}")
        return event

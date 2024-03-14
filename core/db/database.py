import os
import sqlite3
from datetime import datetime

# Assuming environment variables are set externally
DATABASE_PATH = os.getenv('DATABASE_PATH', 'simulation_results.db')


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)


def create_tables():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS parameters (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            iterations INTEGER,
            area REAL,
            thickness REAL,
            porosity REAL,
            water_saturation REAL,
            fvf REAL,
            enabled INTEGER DEFAULT 0, -- 0 for disabled, 1 for enabled
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()


def insert_parameters(config):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO parameters (name, iterations, area, thickness, porosity, water_saturation, fvf, enabled)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)''', config)
        # After inserting a new configuration, disable all others
        last_row_id = cursor.lastrowid
        cursor.execute('UPDATE parameters SET enabled = 0 WHERE id != ?', (last_row_id,))
        conn.commit()


def list_parameters():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, iterations, area, thickness, porosity, water_saturation, created_at, '
                       'updated_at, enabled FROM parameters ORDER BY created_at DESC')
        return cursor.fetchall()


def enable_parameter(config_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE parameters SET enabled = 0')  # Disable all
        cursor.execute('UPDATE parameters SET enabled = 1 WHERE id = ?', (config_id,))
        conn.commit()


def delete_parameter(config_id):
    """Delete a configuration by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM parameters WHERE id = ?", (config_id,))
    conn.commit()
    conn.close()


def activate_parameter(config_id):
    """Activate a configuration, setting it as enabled."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Set all to disabled first, if you want only one active at a time
    cursor.execute("UPDATE parameters SET enabled = 0")
    # Now, activate the selected one
    cursor.execute("UPDATE parameters SET enabled = 1 WHERE id = ?", (config_id,))
    conn.commit()
    conn.close()


def save_parameter(configuration):
    """Save or update a configuration."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # If the configuration has an 'id', update; else, insert a new record
    if 'id' in configuration and configuration['id']:
        cursor.execute("""
            UPDATE parameters
            SET name = ?, iterations = ?, area = ?, thickness = ?, porosity = ?, water_saturation = ?, fvf = ?, updated_at = ?
            WHERE id = ?""",
                       (configuration['name'], configuration['iterations'], configuration['area'],
                        configuration['thickness'],
                        configuration['porosity'], configuration['water_saturation'], configuration['fvf'],
                        datetime.now(), configuration['id']))
    else:
        cursor.execute("""
            INSERT INTO parameters (name, iterations, area, thickness, porosity, water_saturation, fvf, enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                       (configuration['name'], configuration['iterations'], configuration['area'],
                        configuration['thickness'],
                        configuration['porosity'], configuration['water_saturation'], configuration['fvf'], 0))
    conn.commit()
    conn.close()

import os
import sqlite3
from datetime import datetime

# Assuming environment variables are set externally
DATABASE_PATH = os.getenv('DATABASE_PATH', 'simulation_results.db')

form_to_db_column_mapping = {
    "Water Saturation": "water_saturation",
    "FVF": "fvf",
    "Area": "area",
    "Thickness": "thickness",
    "Porosity": "porosity",
    "Iterations": "iterations",
    "Name": "name",
    "Id": "id",
    "Enabled": "enabled",
}


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)


def activate_parameter(config_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE parameters SET enabled = 0")  # Disable all
        cursor.execute("UPDATE parameters SET enabled = 1 WHERE id = ?", (config_id,))
        conn.commit()


def create_tables():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS PARAMETERS (
          ID INTEGER PRIMARY KEY,
          NAME TEXT NOT NULL,
          ITERATIONS INTEGER,
          ENABLED INTEGER DEFAULT 0,
          CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
          UPDATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS DISTRIBUTIONS (
          ID INTEGER PRIMARY KEY,
          PARAMETER_ID INTEGER,
          PARAMETER_NAME TEXT NOT NULL,
          DISTRIBUTION_TYPE TEXT NOT NULL,
          MEAN REAL,
          STD_DEV REAL,
          MIN_VALUE REAL,
          MAX_VALUE REAL,
          MODE_VALUE REAL,
          FOREIGN KEY(PARAMETER_ID) REFERENCES PARAMETERS(ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS SIMULATIONS (
          ID INTEGER PRIMARY KEY,
          PARAMETER_ID INTEGER,
          CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(PARAMETER_ID) REFERENCES PARAMETERS(ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS RESULTS (
          ID INTEGER PRIMARY KEY,
          SIMULATION_ID INTEGER,
          OOIP REAL,
          ROIP REAL,
          RGIP REAL,
          CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(SIMULATION_ID) REFERENCES SIMULATIONS(ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS SIMULATION_STATISTICS (
          ID INTEGER PRIMARY KEY,
          SIMULATION_ID INTEGER,
          MEAN_OOIP REAL,
          MEDIAN_OOIP REAL,
          STD_DEV_OOIP REAL,
          P10_OOIP REAL,
          P50_OOIP REAL, -- Median is the same as P50
          P90_OOIP REAL,
          MEAN_ROIP REAL,
          MEDIAN_ROIP REAL,
          STD_DEV_ROIP REAL,
          P10_ROIP REAL,
          P50_ROIP REAL,
          P90_ROIP REAL,
          MEAN_RGIP REAL,
          MEDIAN_RGIP REAL,
          STD_DEV_RGIP REAL,
          P10_RGIP REAL,
          P50_RGIP REAL,
          P90_RGIP REAL,
          CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(SIMULATION_ID) REFERENCES SIMULATIONS(ID)
        )''')

        conn.commit()


def get_enabled_parameter():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM parameters WHERE enabled = 1 LIMIT 1")
        enabled_param = cursor.fetchone()
        print(enabled_param)
        return enabled_param if enabled_param else []

def get_enabled_parameter_and_distributions():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Fetch the enabled parameter
        cursor.execute("SELECT id, name FROM parameters WHERE enabled = 1 LIMIT 1")
        enabled_param = cursor.fetchone()
        if not enabled_param:
            return None, []

        param_id, param_name = enabled_param

        # Fetch distributions for the enabled parameter
        cursor.execute("""
            SELECT parameter_name, distribution_type, mean, std_dev, min_value, max_value, mode_value
            FROM distributions
            WHERE parameter_id = ?
        """, (param_id,))
        distributions = cursor.fetchall()
        return param_name, distributions

def get_distributions_by_parameter_id(parameter_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.id, d.parameter_id, d.parameter_name, d.distribution_type, d.mean, d.std_dev, d.min_value, d.max_value, d.mode_value, p.iterations
            FROM distributions as d INNER JOIN parameters as p ON d.parameter_id = p.id
            WHERE parameter_id = ?''', (parameter_id,))
        return cursor.fetchall()


def insert_parameters(config):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Insert into parameters table
        cursor.execute('''
            INSERT INTO parameters (name, iterations, enabled)
            VALUES (?, ?, 1)''', (config['Name'], config['Iterations']))
        last_row_id = cursor.lastrowid

        # Disable all others
        cursor.execute('UPDATE parameters SET enabled = 0 WHERE id != ?', (last_row_id,))

        # Insert into distributions table, assume config includes 'distributions' which is a list of distribution dicts
        for distribution in config.get('Distributions', []):
            cursor.execute('''
                INSERT INTO distributions (parameter_id, parameter_name, distribution_type, mean, std_dev, min_value, max_value, mode_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
                last_row_id,
                distribution['Parameter_name'],
                distribution['Distribution_type'],
                distribution.get('Mean', None),
                distribution.get('Std_dev', None),
                distribution.get('Min_value', None),
                distribution.get('Max_value', None),
                distribution.get('Mode_value', None)
            ))

        conn.commit()


def update_parameter_by_id(config_id, new_values):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Update parameters
        cursor.execute('''
            UPDATE parameters
            SET name = ?, iterations = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?''', (new_values['name'], new_values['iterations'], config_id))

        # Example of how to handle distribution updates
        # This assumes a more complex handling based on your application logic

        conn.commit()


def list_parameters():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT p.id, p.name, p.iterations, p.enabled, 
               p.created_at, p.updated_at
        FROM parameters p
        ORDER BY p.created_at DESC
        ''')
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

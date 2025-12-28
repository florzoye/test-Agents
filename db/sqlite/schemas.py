def create_clients_table_sql() -> str:
    return """
    CREATE TABLE IF NOT EXISTS clients (
        tg_id INTEGER PRIMARY KEY,
        message_history TEXT,
        age INTEGER,
        full_name TEXT,
        username TEXT,
        email TEXT,
        instagram_nick TEXT,
        client_project_info TEXT,
        lead_status TEXT DEFAULT 'new'
    )
    """


def insert_client_sql() -> str:
    return """
    INSERT OR IGNORE INTO clients (
        tg_id, message_history, age, full_name, username, 
        email, instagram_nick, client_project_info, lead_status
    )
    VALUES (
        :tg_id, :message_history, :age, :full_name, :username,
        :email, :instagram_nick, :client_project_info, :lead_status
    )
    """


def select_client_sql() -> str:
    return "SELECT * FROM clients WHERE tg_id = :tg_id"


def select_all_clients_sql() -> str:
    return "SELECT * FROM clients"


def delete_client_sql() -> str:
    return "DELETE FROM clients WHERE tg_id = :tg_id"


def delete_all_clients_sql() -> str:
    return "DELETE FROM clients"


def client_exists_sql() -> str:
    return "SELECT 1 FROM clients WHERE tg_id = :tg_id LIMIT 1"


def select_clients_by_status_sql() -> str:
    return "SELECT * FROM clients WHERE lead_status = :status"


def select_message_history_sql() -> str:
    return "SELECT message_history FROM clients WHERE tg_id = :tg_id"


def update_lead_status_sql() -> str:
    return "UPDATE clients SET lead_status = :lead_status WHERE tg_id = :tg_id"


def update_project_info_sql() -> str:
    return "UPDATE clients SET client_project_info = :client_project_info WHERE tg_id = :tg_id"
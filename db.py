import psycopg2

# Подключение к БД
def get_connection():
    return psycopg2.connect(
        dbname="2025_psql_ann",
        user="2025_psql_a_usr",
        password="IGyFd2MU2LsVU5JL",
        host="5.183.188.132",
        port=5432
    )

# Единицы измерения
def get_units():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT "id_единицы", "наименование", "код_единицы"
        FROM "единицы_измерения"
        ORDER BY "id_единицы";
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Категории номенклатуры
def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT "id_категории", "наименование", "описание"
        FROM "категории_номенклатуры"
        ORDER BY "id_категории";
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Номенклатура
def get_nomenclature():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT "id_номенклатуры", "наименование", "id_категории", "id_единицы", "артикул", "описание"
        FROM "номенклатура"
        ORDER BY "id_номенклатуры";
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Сотрудники
def get_employees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT "фамилия", "имя", "отчество", "должность", "телефон", "email"
        FROM "сотрудники"
        ORDER BY "фамилия";
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Контрагенты
def get_contractors():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT "id_контрагента", "наименование", "тип", "менеджер", "телефон", "email", "адрес"
        FROM "контрагенты"
        ORDER BY "id_контрагента";
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Склады
def get_warehouses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT "id_склада", "наименование", "адрес", "вместимость_м2", "ответственный"
        FROM "склады"
        ORDER BY "id_склада";
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

import psycopg2

# Функция подключения
def get_connection():
    return psycopg2.connect(
    dbname="2025_psql_ann",
    user="2025_psql_a_usr",
    password="IGyFd2MU2LsVU5JL",
    host="5.183.188.132",
    port=5432
)

# Получение всех единиц измерения
def get_units():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT "id_единицы", "наименование", "код_единицы" FROM "единицы_измерения"
        ORDER BY "id_единицы";
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

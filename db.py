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
        SELECT "id_unit", "title", "code_unit"
        FROM "units"
        ORDER BY "id_unit";
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
        SELECT "id_category", "title", "description"
        FROM "categories_nomenclature"
        ORDER BY "id_category";
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
        SELECT
            n.id_nomenclature,
            n.title,
            c.title AS category,
            u.code_unit AS unit,
            n.article,
            n.description
        FROM nomenclature n
        JOIN categories_nomenclature c ON n.id_category = c.id_category
        JOIN units u ON n.id_unit = u.id_unit
        ORDER BY n.id_nomenclature;
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
        SELECT "id_employee","familia", "imya", "otchestvo", "position", "phone", "email"
        FROM "employees"
        ORDER BY "familia";
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
        SELECT "id_counterparty", "name", "manager", "phone", "email", "address"
        FROM "counterparties"
        ORDER BY "id_counterparty";
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
        SELECT
            w.id_warehouse,
            w.title,
            w.address,
            w.capacity_m2,
            e.familia || ' ' || e.imya || 
            COALESCE(' ' || e.otchestvo, '') AS responsible
        FROM warehouses w
        LEFT JOIN employees e ON w.responsible = e.id_employee
        ORDER BY w.id_warehouse;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Документы
def get_documents():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            id_document,
            document_type,
            date,
            id_employee,
            number,
            comment,
            is_processed
        FROM document
        ORDER BY date;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Документы прихода
def get_document_prihoda():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            dp.id_document,
            c.name AS counterparty,
            w.title AS warehouse
        FROM document_prihoda dp
        JOIN counterparties c ON dp.id_counterparty = c.id_counterparty
        JOIN warehouses w ON dp.id_warehouse = w.id_warehouse;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Документы расхода
def get_document_rashoda():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            dr.id_document,
            w.title AS warehouse
        FROM document_rashoda dr
        JOIN warehouses w ON dr.id_warehouse = w.id_warehouse;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Документы перемещения
def get_document_peremeshenie():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            dp.id_document,
            w1.title AS warehouse_from,
            w2.title AS warehouse_to
        FROM document_peremeshenie dp
        JOIN warehouses w1 ON dp.id_warehouse_from = w1.id_warehouse
        JOIN warehouses w2 ON dp.id_warehouse_to = w2.id_warehouse;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Номенклатура в документах
def get_nomenclature_document():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            nd.id_document,
            n.title AS nomenclature,
            nd.quantity
        FROM nomenclature_document nd
        JOIN nomenclature n ON nd.id_nomenclature = n.id_nomenclature
        ORDER BY nd.id_document;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Операции по складам
def get_operations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            o.id_operation,
            o.date,
            o.operation_type,
            n.title AS nomenclature,
            o.quantity,
            w.title AS warehouse
        FROM operations o
        JOIN nomenclature n ON o.id_nomenclature = n.id_nomenclature
        JOIN warehouses w ON o.id_warehouse = w.id_warehouse
        ORDER BY o.date;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_prihod_documents_full():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            d.id_document,
            d.number,
            d.date,
            e.familia || ' ' || e.imya AS employee,
            c.name AS counterparty,
            w.title AS warehouse,
            n.title AS nomenclature,
            nd.quantity,
            d.comment,
            d.is_processed
        FROM document d
        JOIN document_prihoda dp ON d.id_document = dp.id_document
        JOIN counterparties c ON dp.id_counterparty = c.id_counterparty
        JOIN warehouses w ON dp.id_warehouse = w.id_warehouse
        JOIN employees e ON d.id_employee = e.id_employee
        JOIN nomenclature_document nd ON d.id_document = nd.id_document
        JOIN nomenclature n ON nd.id_nomenclature = n.id_nomenclature
        ORDER BY d.date;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_rashod_documents_full():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            d.id_document,
            d.number,
            d.date,
            e.familia || ' ' || e.imya AS employee,
            w.title AS warehouse,
            n.title AS nomenclature,
            nd.quantity,
            d.comment,
            d.is_processed
        FROM document d
        JOIN document_rashoda dr ON d.id_document = dr.id_document
        JOIN warehouses w ON dr.id_warehouse = w.id_warehouse
        JOIN employees e ON d.id_employee = e.id_employee
        JOIN nomenclature_document nd ON d.id_document = nd.id_document
        JOIN nomenclature n ON nd.id_nomenclature = n.id_nomenclature
        ORDER BY d.date;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_peremeshchenie_documents_full():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            d.id_document,
            d.number,
            d.date,
            e.familia || ' ' || e.imya AS employee,
            w_from.title AS warehouse_from,
            w_to.title AS warehouse_to,
            n.title AS nomenclature,
            nd.quantity,
            d.comment,
            d.is_processed
        FROM document d
        JOIN document_peremeshenie dp ON d.id_document = dp.id_document
        JOIN warehouses w_from ON dp.id_warehouse_from = w_from.id_warehouse
        JOIN warehouses w_to ON dp.id_warehouse_to = w_to.id_warehouse
        JOIN employees e ON d.id_employee = e.id_employee
        JOIN nomenclature_document nd ON d.id_document = nd.id_document
        JOIN nomenclature n ON nd.id_nomenclature = n.id_nomenclature
        ORDER BY d.date;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_last_operations(limit=10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            o.date,
            o.operation_type,
            n.title AS nomenclature,
            o.quantity,
            w.title AS warehouse
        FROM operations o
        JOIN nomenclature n ON o.id_nomenclature = n.id_nomenclature
        JOIN warehouses w ON o.id_warehouse = w.id_warehouse
        ORDER BY o.date DESC, o.id_operation DESC
        LIMIT %s;
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_operations_full():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            o.date,
            o.operation_type,
            n.title AS nomenclature,
            o.quantity,
            w.title AS warehouse
        FROM operations o
        JOIN nomenclature n ON o.id_nomenclature = n.id_nomenclature
        JOIN warehouses w ON o.id_warehouse = w.id_warehouse
        ORDER BY o.date, n.title;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_stock_balances():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            w.title AS warehouse,
            n.title AS nomenclature,
            u.code_unit AS unit,
            SUM(
                CASE
                    WHEN o.operation_type = 'приход' THEN o.quantity
                    WHEN o.operation_type = 'расход' THEN -o.quantity
                    ELSE 0
                END
            ) AS balance
        FROM operations o
        JOIN warehouses w ON o.id_warehouse = w.id_warehouse
        JOIN nomenclature n ON o.id_nomenclature = n.id_nomenclature
        JOIN units u ON n.id_unit = u.id_unit
        GROUP BY w.title, n.title, u.code_unit
        HAVING SUM(
            CASE
                WHEN o.operation_type = 'приход' THEN o.quantity
                WHEN o.operation_type = 'расход' THEN -o.quantity
                ELSE 0
            END
        ) <> 0
        ORDER BY w.title, n.title;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_turnover_report():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            w.title AS warehouse,
            n.title AS nomenclature,
            u.code_unit AS unit,
            SUM(CASE WHEN o.operation_type='приход' THEN o.quantity ELSE 0 END) AS total_in,
            SUM(CASE WHEN o.operation_type='расход' THEN o.quantity ELSE 0 END) AS total_out,
            SUM(CASE WHEN o.operation_type='приход' THEN o.quantity 
                    WHEN o.operation_type='расход' THEN -o.quantity
                    ELSE 0 END) AS balance
        FROM operations o
        JOIN warehouses w ON o.id_warehouse = w.id_warehouse
        JOIN nomenclature n ON o.id_nomenclature = n.id_nomenclature
        JOIN units u ON n.id_unit = u.id_unit
        GROUP BY w.title, n.title, u.code_unit
        ORDER BY w.title, n.title;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_critical_stock(limit_value=20):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            w.title AS warehouse,
            n.title AS nomenclature,
            u.code_unit AS unit,
            SUM(
                CASE
                    WHEN o.operation_type = 'приход' THEN o.quantity
                    WHEN o.operation_type = 'расход' THEN -o.quantity
                    ELSE 0
                END
            ) AS balance
        FROM operations o
        JOIN warehouses w ON o.id_warehouse = w.id_warehouse
        JOIN nomenclature n ON o.id_nomenclature = n.id_nomenclature
        JOIN units u ON n.id_unit = u.id_unit
        GROUP BY w.title, n.title, u.code_unit
        HAVING SUM(
            CASE
                WHEN o.operation_type = 'приход' THEN o.quantity
                WHEN o.operation_type = 'расход' THEN -o.quantity
                ELSE 0
            END
        ) < %s
        ORDER BY w.title, balance ASC;
    """, (limit_value,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_nomenclature_balance(id_nomenclature, id_warehouse):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(
            CASE
                WHEN o.operation_type = 'приход' THEN o.quantity
                WHEN o.operation_type = 'расход' THEN -o.quantity
                ELSE 0
            END
        ), 0) AS balance
        FROM operations o
        WHERE o.id_nomenclature = %s AND o.id_warehouse = %s
    """, (id_nomenclature, id_warehouse))
    balance = cur.fetchone()[0]
    cur.close()
    conn.close()
    return balance




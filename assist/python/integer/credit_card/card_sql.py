import mysql.connector

# 数据库配置信息
config = {
    'user': 'SpringFlourish',
    'password': '13709891',
    'host': 'localhost',
    'database': 'card_info'
}

# 连接到MySQL数据库
try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # 创建数据库（如果不存在）
    database_name = config['database']
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")

    # 使用新创建的数据库
    cursor.execute(f"USE {database_name}")

    # 创建card_info表
    create_table_query = """
    CREATE TABLE IF NOT EXISTS card_info (
        card_name VARCHAR(50) PRIMARY KEY,
        card_num VARCHAR(20),
        date_valid DATE,
        bill_day SMALLINT,
        pay_day SMALLINT
    )
    """

    cursor.execute(create_table_query)

    print("Table created successfully")

except mysql.connector.Error as error:
    print(f"Failed to create table in MySQL: {error}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
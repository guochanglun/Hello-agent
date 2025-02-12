import os
from typing import List

import pymysql
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, BaseMessage

from model.model import GclModel

llm = GclModel()


def extract_sql_from_file(file_path: str) -> BaseMessage:
    """
    从文件中提取SQL语句
    Args:
        file_path: 文件路径（支持.java/.xml/.log）
    Returns:
        List[str]: AI 解析后的结果，保留 MyBatis 的动态标签
    """
    with open(file_path, 'r') as f:
        content = f.read()
        message = HumanMessage(f"""
            从下面中提取SQL语句，最终返回SQL列表。
            ```
            ${content}
            ```
            
            json示例:
            [sql 语句]
            """)
        response = llm.invoke([message])
    return response


def get_table_structure(table_name):
    """
    查询指定表的表结构
    :param table_name: 表名
    :return: 表结构信息
    """
    db_config = get_db_config()
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 查询表结构
            sql = f"DESCRIBE {table_name};"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


def get_table_indexes(table_name):
    """
    查询指定表的索引信息
    :param table_name: 表名
    :return: 表的索引信息
    """
    db_config = get_db_config()
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 查询表索引信息
            sql = f"SHOW INDEX FROM {table_name};"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


def get_table_row_count(table_name):
    """
    查询指定表的总数据量
    :param table_name: 表名
    :return: 数据量
    """
    db_config = get_db_config()
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 查询数据量
            sql = f"SELECT COUNT(*) AS row_count FROM {table_name};"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result[0]
    finally:
        connection.close()


def explain_sql_query(sql_query):
    """
    对指定的 SQL 语句执行 EXPLAIN 并返回结果
    :param sql_query: SQL 查询语句
    :return: EXPLAIN 结果
    """
    db_config = get_db_config()
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 执行 EXPLAIN
            explain_sql = f"EXPLAIN {sql_query}"
            cursor.execute(explain_sql)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


def save_to_file(filename, content):
    """
    将内容保存到本地文件。

    参数:
    filename (str): 要保存的文件名（包括路径）。
    content (str): 要保存的文件内容。
    """
    try:
        # 打开文件并写入内容
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"文件已成功保存到: {filename}")
    except Exception as e:
        print(f"保存文件时出错: {e}")


# 获取数据库配置
def get_db_config():
    # 加载 .env 文件中的环境变量到系统环境变量中
    load_dotenv()
    # 从环境变量中获取数据库配置
    config = {
        "host": os.getenv("MYSQL_HOST"),
        "port": int(os.getenv("MYSQL_PORT")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE")
    }

    # 检查是否存在配置中的关键字段
    # 记录错误信息，提示用户检查环境变量
    if not all([config["user"], config["password"], config["database"]]):
        # 抛出一个 ValueError 异常，终止函数的执行
        raise ValueError("Missing required database configuration")

    # 配置完整，则返回包含数据库配置的字典config
    return config


if __name__ == '__main__':
    response = extract_sql_from_file("/Users/guochanglun/erp-mdm/erp-mdm-dao/src/main/resources/base/sql-mapper/BpmMapper.xml")
    response.pretty_print()
#     print(get_table_structure('mdm_material_his'))
#     print(get_table_indexes('mdm_material_his'))
#     print(get_table_row_count('mdm_material_his'))
#     print(explain_sql_query('select * from mdm_material_his where id > 9990'))

from typing import List

from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

llm = ChatOpenAI(openai_api_base='https://api.deepseek.com',
                 openai_api_key=SecretStr('sk-84f2ed3716b948e4a6e20dfc2540b7ad'),
                 model_name='deepseek-chat', verbose=True)


@tool
def extract_sql_from_file(file_path: str) -> AIMessage:
    """
    使用OpenAI从文件中提取SQL语句
    Args:
        file_path: 文件路径（支持.java/.xml/.log）
    Returns:
        List[str]: AI 解析后的结果
    """
    with open(file_path, 'r') as f:
        content = f.read()
        message = HumanMessage(f"""
            从下面中提取SQL语句，最终返回SQL列表。
            ```
            ${content}
            ```
            """)
        response = llm.invoke([message])
    # print(f"extract_sql_from_file, {file_path}, {response}")
    response.pretty_print()
    return response


@tool
def detect_sql_anti_pattern(sql: str) -> AIMessage:
    """
    使用OpenAI检测SQL中的语法风险模式
    Args:
        sql: SQL语句
    Returns:
        dict: 风险标签及置信度
    """
    message = HumanMessage(f"""
    从SQL语句的角度判断SQL存在慢查询的风险，给出风险概率，从0%-100%。不考虑数据库负载极高、锁竞争激烈、网络延迟的场景，只考虑SQL执行时的风险，比如如果 in 语句太大就可能慢查询。
    结果字数在80字以内，包括SQL语句、风险概率、风险描述、优化建议。
    
    SQL语句如下，
    ```
    ${sql}
    ```
    """)
    response = llm.invoke([message])
    # print(f"detect_sql_anti_pattern, {sql}, {response}")
    response.pretty_print()
    return response


@tool
def explain_sql_execution_plan(sql: str) -> dict:
    """
    执行EXPLAIN获取风险指标
    Returns:
        dict: 执行计划分析结果
    """
    # 模拟返回数据示例
    print(f"explain_sql_execution_plan, {sql}")
    return {
        "type": "ALL" if "WHERE" not in sql else "INDEX",
        "rows": 100000 if "LIMIT 100000" in sql else 100,
        "extra": ["Using filesort"] if "ORDER BY" in sql else []
    }


# 工具3：表数据量评估（模拟查询）
@tool
def evaluate_table_size(table_name: str) -> int:
    """
    查询表行数
    """
    # 示例数据
    table_sizes = {
        "orders": 5000000,
        "users": 100000
    }
    print(f"evaluate_table_size, {table_name}")
    return table_sizes.get(table_name, 0)

@tool
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
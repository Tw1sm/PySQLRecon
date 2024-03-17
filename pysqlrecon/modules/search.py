import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "search"
HELP = "[bright_black][NORM][/] Keyword search column names for all tables within a database [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    ctx: typer.Context,
    keyword: str = typer.Option(..., '--keyword', help='Keyword to search for')):
    
    pysqlrecon: PySqlRecon = ctx.obj['pysqlrecon']
    use_basic_tables = ctx.obj['basic_tables']

    # verify opts are compatible with module before connecting
    if not PySqlRecon.validate_opts(
        LINK_COMPATIBLE,
        IMPERSONATE_COMPATIBLE,
        pysqlrecon.link,
        pysqlrecon.impersonate
    ):
        exit()

    pysqlrecon.connect()

    if pysqlrecon.link is not None:
        logger.info(f"Searching for columns containing '{keyword}' in '{pysqlrecon.db}' on {pysqlrecon.link} via {pysqlrecon.target}")
    else:
        logger.info(f"Searching for columns containing '{keyword}' in '{pysqlrecon.db}' on {pysqlrecon.target}")
    
    if pysqlrecon.link:
        query = "SELECT table_name, column_name " \
            f"FROM {pysqlrecon.db}.INFORMATION_SCHEMA.COLUMNS WHERE column_name LIKE '%{keyword}%';"
    else:
        query = "SELECT table_name, column_name " \
            f"FROM INFORMATION_SCHEMA.COLUMNS WHERE column_name LIKE '%{keyword}%';"

    pysqlrecon.query_handler(query, use_rpc_query=True)
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()

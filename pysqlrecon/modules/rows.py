import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "rows"
HELP = "[bright_black][NORM][/] Get the count of rows in a table [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    ctx: typer.Context,
    table:  str = typer.Option(..., '--table', help='Table name', rich_help_panel='SQL Options')):
    
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
        logger.info(f"Getting row count of table '{table}' in '{pysqlrecon.db}' on {pysqlrecon.link} via {pysqlrecon.target}")
    else:
        logger.info(f"Getting row count of table '{table}' in '{pysqlrecon.db}' on {pysqlrecon.target}")
    
    query = f"use {pysqlrecon.db}; SELECT COUNT(*) as row_count FROM {table};"
    pysqlrecon.query_handler(query, use_rpc_query=True)
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
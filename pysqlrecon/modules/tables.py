import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "tables"
HELP = "[bright_black][NORM][/] Enumerate tables within a database [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    
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
        logger.info(f"Enumerating tables in '{pysqlrecon.db}' on {pysqlrecon.link} via {pysqlrecon.target}")
    else:
        logger.info(f"Enumerating tables in '{pysqlrecon.db}' on {pysqlrecon.target}")

    
    query = f"SELECT * FROM {pysqlrecon.db}.INFORMATION_SCHEMA.TABLES;"
    pysqlrecon.query_handler(query)
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
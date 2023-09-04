import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "users"
HELP = "[bright_black][NORM][/] Enumerate users with database access [I,L]"
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
        logger.info(f"Enumerating users in the '{pysqlrecon.db}' database on {pysqlrecon.link} via {pysqlrecon.target}")
    else:
        logger.info(f"Enumerating users in the '{pysqlrecon.db}' database on {pysqlrecon.target}")
    
    query = "SELECT name AS username, create_date, " \
            "modify_date, type_desc AS type, authentication_type_desc AS " \
            f"authentication_type FROM {pysqlrecon.db}.sys.database_principals WHERE type NOT " \
            "IN ('A', 'R', 'X') AND sid IS NOT null ORDER BY username;"
    
    pysqlrecon.query_handler(query)
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()

import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "logons"
HELP = "[bright_black][NORM][/] Display SCCM clients and last logged on user [I]"
LINK_COMPATIBLE = False
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(
    ctx:    typer.Context,
    user:   str = typer.Option(None, "--user", help="Filter by username (use % for wildcard)"),
    host:   str = typer.Option(None, "--host", help="Filter by hostname (use % for wildcard)")):
    
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

    if pysqlrecon.db == 'master':
        logger.warning("You likely need to specify the CM_[SITE] database")

    pysqlrecon.connect()

    logger.info("Querying clients and last logged on users")

    query = "select Name00, Username00 from [dbo].[Computer_System_DATA]"
    
    if user and host:
        query += f" where Username00 like '{user}' and Name00 like '{host}'"
    
    elif user:
        logger.debug(f"Filtering on user: {user}")
        query += f" where Username00 like '{user}'"
    
    elif host:
        logger.debug(f"Filtering on host: {host}")
        query += f" where Name00 like '{host}'"

    pysqlrecon.query_handler(query)
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
    

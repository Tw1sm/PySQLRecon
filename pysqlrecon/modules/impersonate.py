import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "impersonate"
HELP = "[bright_black][NORM][/] Enumerate users that can be impersonated"
LINK_COMPATIBLE = False
IMPERSONATE_COMPATIBLE = False


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
        logger.info(f"Enumerating users that can be impersonated on {pysqlrecon.link} via {pysqlrecon.target}")
    else:
        logger.info(f"Enumerating users that can be impersonated on {pysqlrecon.target}")

    query = "SELECT distinct b.name FROM sys.server_permissions a " \
            "INNER JOIN sys.server_principals b ON a.grantor_principal_id " \
            "= b.principal_id WHERE a.permission_name = 'IMPERSONATE';"

    pysqlrecon.query_handler(query)
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
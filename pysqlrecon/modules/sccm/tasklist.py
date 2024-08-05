import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "tasklist"
HELP = "[bright_black][NORM][/] Display task sequences [I]"
LINK_COMPATIBLE = False
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

    if pysqlrecon.db == 'master':
        logger.warning("You likely need to specify the CM_[SITE] database")
    
    pysqlrecon.connect()

    logger.info("Listing SCCM Sites")

    query = "select PkgID, Name from [dbo].[vSMS_TaskSequencePackage]"
    
    pysqlrecon.query_handler(query)
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "users"
HELP = "[bright_black][NORM][/] Enumerate SCCM users [I]"
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
    
    #
    # High-Level SCCM User Listing
    #
    logger.info("High-Level SCCM User Listing")
    query = "select LogonName, AdminID, SourceSite, DistinguishedName from [dbo].[RBAC_Admins]"
    pysqlrecon.query_handler(query)
    pysqlrecon.print_results(use_basic_tables)

    #
    # Detailed Permissions
    #
    logger.info("Detailed Permissions")
    query = "select LogonName, RoleName from [dbo].[v_SecuredScopePermissions]"
    pysqlrecon.query_handler(query)
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
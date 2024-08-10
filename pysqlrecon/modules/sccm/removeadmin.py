import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "removeadmin"
HELP = "[red][PRIV][/] Remove elevated account or elevated privileges [I]"
LINK_COMPATIBLE = False
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(
    ctx:            typer.Context,
    id:             str = typer.Option(..., "--adminid", help="AdminID of the user to demote/remove"),
    permissions:    str = typer.Option("00000000|00000000", "--permissions", help="Permissions to remove (default will remove all permissions and account)")):
    
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

    rm_account = True if "00000000|00000000" in permissions else False

    values = ''
    privs_added = False
    
    if "SMS00ALL|SMS0001R" in permissions or rm_account:
        values += f"(AdminID={id} and ScopeID = 'SMS00ALL' and RoleID = 'SMS0001R' and ScopeTypeID = '29')"
        privs_added = True

    if "SMS00004|SMS0001R" in permissions or rm_account:
        if privs_added:
            values += " or "
        values += f"(AdminID={id} and ScopeID = 'SMS00004' and RoleID = 'SMS0001R' and ScopeTypeID = '1')"
        privs_added = True

    if "SMS00001|SMS0001R" in permissions or rm_account:
        if privs_added:
            values += " or "
        values += f"(AdminID={id} and ScopeID = 'SMS00001' and RoleID = 'SMS0001R' and ScopeTypeID = '1')"

    if values == '':
        logger.warning("No permissions, or invalid permissions, specified")
        exit()
    
    pysqlrecon.connect()
    
    #
    # Remove permissions
    #
    logger.info(f"Removing permissions from AdminID {id}")
    query = "Delete from [dbo].[RBAC_ExtendedPermissions] where " + values
    logger.debug(f"Constructed delete privs statement: {query}")

    pysqlrecon.query_handler(query)
    if len(pysqlrecon.ms_sql.rows) > 0:
        logger.error("Failed to remove permissions")
        logger.error(pysqlrecon.get_last_resp())
        pysqlrecon.disconnect()
        exit()

    logger.info(f"Removed permissions from AdminID {id}")

    #
    # Remove account
    #
    if rm_account:
        query = f"Delete from [dbo].[RBAC_Admins] where AdminID={id}"
        pysqlrecon.query_handler(query)

        if len(pysqlrecon.ms_sql.rows) > 0:
            logger.error("Failed to remove account")
            logger.error(pysqlrecon.get_last_resp())
            pysqlrecon.disconnect()
            exit()
        
        logger.info(f"Removed account with AdminID {id}")

    pysqlrecon.disconnect()
    

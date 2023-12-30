import typer

from pysqlrecon.logger import logger, console, OBJ_EXTRA_FMT
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "whoami"
HELP = "[bright_black][NORM][/] Gather logged in user, mapped user and roles [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True

DEFAULT_ROLES = ["sysadmin", "setupadmin", "serveradmin", "securityadmin",
                    "processadmin", "diskadmin", "dbcreator", "bulkadmin"]

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    
    pysqlrecon: PySqlRecon = ctx.obj['pysqlrecon']

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
        logger.info(f"Determining user permissions on {pysqlrecon.link} via {pysqlrecon.target}")
    else:
        logger.info(f"Determining user permissions on {pysqlrecon.target}")

    pysqlrecon.query_handler("SELECT SYSTEM_USER;")
    logger.info(f"Logged in as [cyan]{pysqlrecon.get_last_resp()}[/]", extra=OBJ_EXTRA_FMT)
    
    pysqlrecon.query_handler("SELECT USER_NAME();")
    logger.info(f"Mapped to the user [cyan]{pysqlrecon.get_last_resp()}[/]", extra=OBJ_EXTRA_FMT)

    logger.info("Gathering roles:")
    pysqlrecon.query_handler("SELECT [name] FROM sysusers WHERE issqlrole = 1;")
    roles = [row['name'] for row in pysqlrecon.ms_sql.rows]
    
    logger.debug(f"Identified {len(roles)} database roles")
    logger.debug(f"Roles: {roles}")
    
    print()

    # db-specific roles    
    for role in roles:
        pysqlrecon.query_handler(f"SELECT IS_MEMBER('{role}');")
        check_role(role, pysqlrecon.get_last_resp())

    # check server roles
    for role in DEFAULT_ROLES:
        pysqlrecon.query_handler(f"SELECT IS_SRVROLEMEMBER('{role}');")
        check_role(role, pysqlrecon.get_last_resp())


    print()
    pysqlrecon.disconnect()


def check_role(role, last_resp):
    if last_resp == 1:
        console.print(f"{' |->':>15} User is a member of the [green]{role}[/] role")
    else:
        console.print(f"{' |->':>15} User is NOT a member of the [red]{role}[/] role")
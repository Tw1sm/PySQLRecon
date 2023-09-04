import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "xpcmd"
HELP = "[red][PRIV][/] Execute a system command using xp_cmdshell [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    command: str = typer.Option(..., '--command', help='Command to execute')):
    
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
    
    logger.info("Executing system command...")

    if pysqlrecon.link is not None:
        if pysqlrecon.linked_check_module("xp_cmdshell"):
            pysqlrecon.xpcmd(command)
            logger.info("Command executed (Output not returned for linked server cmd execution)")
        else:
            logger.warning(f"xp_cmdshell is not enabled on {pysqlrecon.link}")

    else:
        if pysqlrecon.check_module("xp_cmdshell"):
            pysqlrecon.xpcmd(command)
            pysqlrecon.print_results(use_basic_tables)
        else:
            logger.warning("xp_cmdshell is not enabled")

    pysqlrecon.disconnect()
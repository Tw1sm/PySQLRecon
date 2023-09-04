import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "template"
HELP = "[bright_black][NORM][/] <COMMAND HELP> [I,L]"
#HELP = "[red][PRIV][/] <COMMAND HELP> [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    opt1: str = typer.Option(..., '--opt1', help='<HELP>'),
    opt2: str = typer.Option(None, '--op2', help='<HELP>')):
    
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

    # command logic
    
    pysqlrecon.disconnect()
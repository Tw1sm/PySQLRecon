import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "disableclr"
HELP = "[red][PRIV][/] Disable CLR integration [I,L]"
LINK_COMPATIBLE = True
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

    pysqlrecon.connect()

    if pysqlrecon.link is not None:        
        pysqlrecon.validate_link()

        logger.info(f"Disabling CLR integration on {pysqlrecon.link} via {pysqlrecon.target}")
        pysqlrecon.linked_module_toggle("clr enabled", "0")

        pysqlrecon.linked_check_module("clr enabled")
        pysqlrecon.print_results(use_basic_tables)

    else:
        logger.info(f"Disabling CLR integration on {pysqlrecon.target}")
        pysqlrecon.module_toggle("clr enabled", "0")
        pysqlrecon.check_module("clr enabled")
        pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
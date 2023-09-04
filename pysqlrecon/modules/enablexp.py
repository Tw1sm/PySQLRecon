import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "enablexp"
HELP = "[red][PRIV][/] Enable xp_cmdshell [I,L]"
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
        if not pysqlrecon.validate_link():
            logger.warning(f"{pysqlrecon.link} is not a linked server")
            pysqlrecon.disconnect()
            exit()

        logger.info(f"Enabling xp_cmdshell on {pysqlrecon.link} via {pysqlrecon.target}")
        pysqlrecon.linked_module_toggle("xp_cmdshell", "1")

        pysqlrecon.linked_check_module("xp_cmdshell")
        pysqlrecon.print_results(use_basic_tables)

    else:
        logger.info(f"Enabling xp_cmdshell on {pysqlrecon.target}")
        pysqlrecon.module_toggle("xp_cmdshell", "1")
        pysqlrecon.check_module("xp_cmdshell")
        pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
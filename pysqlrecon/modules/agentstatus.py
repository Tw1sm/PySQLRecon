import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "agentstatus"
HELP = "[red][PRIV][/] Enumerate SQL agent status and jobs [I,L]"
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
        logger.info(f"Getting SQL agent status on {pysqlrecon.link} via {pysqlrecon.target}")
    else:
        logger.info(f"Getting SQL agent status on {pysqlrecon.target}")
    
    
    if not pysqlrecon.get_agent_status():
        logger.warning("SQL agent is not running")
        pysqlrecon.disconnect()
        exit()
    
    logger.info("SQL agent is running")
    
    if pysqlrecon.link is not None:
        logger.info(f"Agent jobs on {pysqlrecon.link}")
    else:
        logger.info(f"Agent jobs on {pysqlrecon.target}")

    pysqlrecon.get_agent_jobs()
    pysqlrecon.print_results(use_basic_tables)

    pysqlrecon.disconnect()
import typer

from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "agentcmd"
HELP = "[red][PRIV][/] Execute a system command using agent jobs [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    command: str = typer.Option(..., '--command', help='Command to execute'),
    job_name: str = typer.Option(None, '--job', help='Agent job name to use (instead of randomly generated string)'),
    step_name: str = typer.Option(None, '--step', help='Agent step name to use (instead of randomly generated string)')):
    
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
        logger.info(f"Executing command in SQL Agent job on {pysqlrecon.link} via {pysqlrecon.target}")
    else:
        logger.info(f"Executing command in SQL Agent job on  {pysqlrecon.target}")

    if not pysqlrecon.get_agent_status():
        logger.warning("SQL agent is not running")
        pysqlrecon.disconnect()
        exit()

    if pysqlrecon.link is not None:
        if not pysqlrecon.check_rpc_on_link(pysqlrecon.link):
            logger.warning(f"RPC needs to enabled on {pysqlrecon.link}")
            pysqlrecon.disconnect()
            exit()

    job = pysqlrecon.add_agent_job(command, job_name, step_name)    
    
    pysqlrecon.get_agent_jobs()
    pysqlrecon.print_results(use_basic_tables)

    if job not in [item['name'] for item in pysqlrecon.ms_sql.rows if 'name' in item]:
        logger.warning(f"Error adding SQL agent job - {job} not found")
        pysqlrecon.disconnect()
        exit()


    logger.info(f"Executing job {job} and waiting 5 seconds...")
    pysqlrecon.exec_agent_job(job)
    pysqlrecon.delete_agent_job(job)

    logger.info(f"Deleted job {job}")

    pysqlrecon.get_agent_jobs()
    pysqlrecon.print_results(use_basic_tables)
    
    pysqlrecon.disconnect()
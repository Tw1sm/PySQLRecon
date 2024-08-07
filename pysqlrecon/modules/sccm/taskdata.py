import typer

from pysqlrecon.logger import logger, console
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "taskdata"
HELP = "[bright_black][NORM][/] Decrypt task sequences [I]"
LINK_COMPATIBLE = False
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

    if pysqlrecon.db == 'master':
        logger.warning("You likely need to specify the CM_[SITE] database")
    
    pysqlrecon.connect()

    logger.info("Gathering encrypted task sequence blobs")

    query = "select PkgID, Name, Sequence from [dbo].[vSMS_TaskSequencePackage]"
    
    pysqlrecon.query_handler(query)
    
    if len(pysqlrecon.ms_sql.rows) == 0:
        logger.warning("No results found")
        return
    
    logger.info(f"Found {len(pysqlrecon.ms_sql.rows)} task sequences")
    
    #
    # Expecting PkgID | Name | Sequence
    # 
    for row in pysqlrecon.ms_sql.rows:
        logger.info(f"Task Sequence ID: {row['PkgID']}")
        logger.info(f"Task Sequence Name: \"{row['Name']}\"")

        # convert hex to byte list
        hex_str = row['Sequence'].decode('ascii')
        encrypted_blob = bytes.fromhex(hex_str).decode('ascii')
        logger.debug("Decrypting blob...")
        xml_task = pysqlrecon.decode_data(bytes.fromhex(encrypted_blob))

        console.print()
        console.print(xml_task)
        console.print()

    pysqlrecon.disconnect()
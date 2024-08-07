import typer
from pysqlrecon.logger import init_logger, logger
from pysqlrecon.lib import PySqlRecon
from pysqlrecon.modules import __all__
from pysqlrecon import __version__

app = typer.Typer(
    add_completion=False,
    rich_markup_mode='rich',
    context_settings={'help_option_names': ['-h', '--help']},
    pretty_exceptions_show_locals=False
)

for command in __all__:
    app.add_typer(
        command.app,
        name=command.COMMAND_NAME,
        help=command.HELP
    )


@app.callback(no_args_is_help=True)
def main(
    # context for passing global args
    ctx: typer.Context,
    
    # SQL Options
    port: int = typer.Option(1433, '--port', help='Target MSSQL port', rich_help_panel='SQL Options'),
    db: str = typer.Option('master', '--database', help='Database name to authenticate to or query', rich_help_panel='SQL Options'),
    link: str = typer.Option(None, '--link', help='Linked server hostname', rich_help_panel='SQL Options'),
    impersonate: str = typer.Option(None, '--impersonate', help='Impersonate a user', rich_help_panel='SQL Options'),

    # Authentication Options
    usernname: str = typer.Option(..., '--username', '-u', help='Username', rich_help_panel='Authentication Options'),
    password: str = typer.Option(None, '--password', '-p', help='Password', rich_help_panel='Authentication Options'),
    domain: str = typer.Option(None, '--domain', '-d', help='Domain', rich_help_panel='Authentication Options'),
    target: str = typer.Option(..., '--target', '-t', help='Target SQL server hostname or IP address', rich_help_panel='Authentication Options'),
    sql_auth: bool = typer.Option(False, '--sql-auth', help='Use SQL authentication', rich_help_panel='Authentication Options'),
    hashes: str = typer.Option(None, '--hashes', metavar="LMHASH:NTHASH", help='NTLM hashes, format is LMHASH:NTHASH', rich_help_panel='Authentication Options'),
    no_pass: bool = typer.Option(False, '--no-pass', help='Don\'t ask for password (useful for -k)', rich_help_panel='Authentication Options'),
    kerberos: bool = typer.Option(False, '-k', '--kerberos', help='Use Kerberos authentication. Grabs credentials from ccache file '
                                        '(KRB5CCNAME) based on target parameters', rich_help_panel='Authentication Options'),
    aesKey: str = typer.Option(None, '--aesKey', help='AES key to use for Kerberos Authentication (128 or 256 bits)', rich_help_panel='Authentication Options'),
    dc_ip: str = typer.Option('', '--dc-ip', help='Domain controller IP or hostname', rich_help_panel='Authentication Options'),
    
    # Misc Options
    debug: bool = typer.Option(False, '--debug', help='Turn DEBUG output ON', rich_help_panel='Misc Options'),
    basic_tables: bool = typer.Option(False, '--basic-tables', help='Use simple ASCII table output (avoids truncation)', rich_help_panel='Misc Options'),
    quiet: bool = typer.Option(False, '--quiet', help='Hide the banner', rich_help_panel='Misc Options')):

    if not quiet:
        banner()

    init_logger(debug)

    if impersonate is not None and link is not None:
        logger.warning("Cannot use --impersonate and --link together")
        exit()

    if not sql_auth and domain is None:
        logger.warning("Windows authentication requires a domain specified with -d/--domain")
        exit()

    # accesing a link may require Kerberos auth
    if link is not None and kerberos is False:
        logger.warning("Querying a linked server may require specifying Kerberos authentication")

    windows_auth = True if sql_auth is False else False
    pysqlrecon = PySqlRecon(
        target,
        domain,
        usernname,
        password,
        port,
        link,
        impersonate,
        db,
        hashes,
        aesKey,
        kerberos,
        no_pass,
        dc_ip,
        windows_auth
    )

    ctx.obj = {
        'pysqlrecon': pysqlrecon,
        'basic_tables': basic_tables
    }


def banner():
    print(f'''                                       
        _____     _____ _____ __    _____                 
       |  _  |_ _|   __|     |  |  | __  |___ ___ ___ ___ 
       |   __| | |__   |  |  |  |__|    -| -_|  _| . |   |
       |__|  |_  |_____|__  _|_____|__|__|___|___|___|_|_|  v{__version__}
             |___|        |__|                            
    ''')


if __name__ == '__main__':
    app(prog_name='pysqlrecon')

import typer

from pysqlrecon.logger import logger, console
from pysqlrecon.lib import PySqlRecon

app = typer.Typer()
COMMAND_NAME = "info"
HELP = "[bright_black][NORM][/] Gather information about the SQL server"
LINK_COMPATIBLE = False
IMPERSONATE_COMPATIBLE = False


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    
    info = {
        'ComputerName': '',
        'DomainName': '',
        'ServicePid': '',
        'ServiceName': '',
        'ServiceAccount': '',
        'AuthenticationMode': '',
        'ForcedEncryption': '',
        'Clustered': '',
        'SqlServerVersionNumber': '',
        'SqlServerMajorVersion': '',
        'SqlServerEdition': '',
        'SqlServerServicePack': '',
        'OsArchitecture': '',
        'OsMachineType': '',
        'OsVersion': '',
        'OsVersionNumber': '',
        'CurrentLogin': '',
        'IsSysAdmin': '',
        'ActiveSessions': ''
    }
    
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

    logger.info("Extracting SQL server information")

    pysqlrecon.query_handler("SELECT IS_SRVROLEMEMBER('sysadmin');")
    if pysqlrecon.get_last_resp() == 1:
        info['IsSysAdmin'] = True
        logger.debug("User is sysadmin")
    else:
        info['IsSysAdmin'] = False
        # these require sysadmin in SQLRecon
        del info['OsMachineType']
        del info['OsVersion']

        logger.debug("User is not sysadmin")
    
    ####
    # ComputerName
    pysqlrecon.query_handler("SELECT @@SERVERNAME;")
    info['ComputerName'] = pysqlrecon.get_last_resp()

    ####
    # DomainName
    pysqlrecon.query_handler("SELECT default_domain();")
    info['DomainName'] = pysqlrecon.get_last_resp()

    ####
    # ServicePid
    query = "SELECT CONVERT(VARCHAR(255), SERVERPROPERTY('processid'));"
    pysqlrecon.query_handler(query)
    info['ServicePid'] = pysqlrecon.get_last_resp().decode('utf-8')

    ####
    # ServiceName
    query = "DECLARE @SQLServerServiceName varchar(250)\n" \
            "DECLARE @SQLServerInstance varchar(250)\n" \
            "if @@SERVICENAME = 'MSSQLSERVER'\n" \
            "BEGIN\n" \
            "set @SQLServerInstance = 'SYSTEM\CurrentControlSet\Services\MSSQLSERVER'\n" \
            "set @SQLServerServiceName = 'MSSQLSERVER'\n" \
            "END\n" \
            "ELSE\n" \
            "BEGIN\n" \
            "set @SQLServerInstance = 'SYSTEM\CurrentControlSet\Services\MSSQL$'+cast(@@SERVICENAME as varchar(250))\n" \
            "set @SQLServerServiceName = 'MSSQL$'+cast(@@SERVICENAME as varchar(250))\n" \
            "END\n" \
            "SELECT @SQLServerServiceName;"
    pysqlrecon.query_handler(query)
    info['ServiceName'] = pysqlrecon.get_last_resp().decode('utf-8')

    ####
    # ServiceAccount
    query = "DECLARE @SQLServerInstance varchar(250)\n" \
            "if @@SERVICENAME = 'MSSQLSERVER'\n" \
            "BEGIN\n" \
            "set @SQLServerInstance = 'SYSTEM\CurrentControlSet\Services\MSSQLSERVER'\n" \
            "END\n" \
            "ELSE\n" \
            "BEGIN\n" \
            "set @SQLServerInstance = 'SYSTEM\CurrentControlSet\Services\MSSQL$'+cast(@@SERVICENAME as varchar(250))\n" \
            "END\n" \
            "DECLARE @ServiceAccountName varchar(250)\n" \
            "EXECUTE master.dbo.xp_instance_regread\n" \
            "N'HKEY_LOCAL_MACHINE', @SQLServerInstance,\n" \
            "N'ObjectName',@ServiceAccountName OUTPUT, N'no_output'\n" \
            "SELECT @ServiceAccountName;"
    
    pysqlrecon.query_handler(query)
    info['ServiceAccount'] = pysqlrecon.get_last_resp().decode('utf-8')

    ####
    # AuthenticationMode
    query = "DECLARE @AuthenticationMode INT\n" \
            "EXEC master.dbo.xp_instance_regread N'HKEY_LOCAL_MACHINE',\n" \
            "N'Software\Microsoft\MSSQLServer\MSSQLServer',\n" \
            "N'LoginMode', @AuthenticationMode OUTPUT\n" \
            "(SELECT CASE @AuthenticationMode\n" \
            "WHEN 1 THEN 'Windows Authentication'\n" \
            "WHEN 2 THEN 'Windows and SQL Server Authentication'\n" \
            "ELSE 'Unknown'\n" \
            "END);"
    pysqlrecon.query_handler(query)
    info['AuthenticationMode'] = pysqlrecon.get_last_resp().decode('utf-8')

    ####
    # ForcedEncryption
    query = "BEGIN TRY\n" \
            "DECLARE @ForcedEncryption INT\n" \
            "EXEC master.dbo.xp_instance_regread N'HKEY_LOCAL_MACHINE',\n" \
            "N'SOFTWARE\MICROSOFT\Microsoft SQL Server\MSSQLServer\SuperSocketNetLib',\n" \
            "N'ForceEncryption', @ForcedEncryption OUTPUT\n" \
            "END TRY\n" \
            "BEGIN CATCH	            \n" \
            "END CATCH\n" \
            "SELECT @ForcedEncryption;"
    pysqlrecon.query_handler(query)
    info['ForcedEncryption'] = pysqlrecon.get_last_resp()

    ####
    # Clustered
    query = "SELECT CASE  SERVERPROPERTY('IsClustered')\n" \
            "WHEN 0\n" \
            "THEN 'No'\n" \
            "ELSE 'Yes'\n" \
            "END"
    pysqlrecon.query_handler(query)
    info['Clustered'] = pysqlrecon.get_last_resp().decode('utf-8')

    ####
    # SqlServerVersionNumber
    query = "SELECT CONVERT(VARCHAR(255), SERVERPROPERTY('productversion'));"
    pysqlrecon.query_handler(query)
    info['SqlServerVersionNumber'] = pysqlrecon.get_last_resp().decode('utf-8')

    ####
    # SqlServerMajorVersion
    query = "SELECT SUBSTRING(@@VERSION, CHARINDEX('2', @@VERSION), 4);"
    pysqlrecon.query_handler(query)
    info['SqlServerMajorVersion'] = pysqlrecon.get_last_resp()

    ####
    # SqlServerEdition
    query = "SELECT CONVERT(VARCHAR(255), SERVERPROPERTY('Edition'));"
    pysqlrecon.query_handler(query)
    info['SqlServerEdition'] = pysqlrecon.get_last_resp().decode('utf-8')

    ####
    # SqlServerServicePack
    query = "SELECT CONVERT(VARCHAR(255), SERVERPROPERTY('ProductLevel'));"
    pysqlrecon.query_handler(query)
    info['SqlServerServicePack'] = pysqlrecon.get_last_resp().decode('utf-8')

    ####
    # OsArchitecture
    query = "SELECT SUBSTRING(@@VERSION, CHARINDEX('x', @@VERSION), 3);"
    pysqlrecon.query_handler(query)
    info['OsArchitecture'] = pysqlrecon.get_last_resp()

    ####
    # OsMachineType
    if info['IsSysAdmin']:
        query = "DECLARE @MachineType  SYSNAME\n" \
                "EXECUTE master.dbo.xp_regread\n" \
                "@rootkey		= N'HKEY_LOCAL_MACHINE',\n" \
                "@key			= N'SYSTEM\CurrentControlSet\Control\ProductOptions',\n" \
                "@value_name		= N'ProductType',\n" \
                "@value			= @MachineType output\n" \
                "SELECT @MachineType;"
        pysqlrecon.query_handler(query)
        info['OsMachineType'] = pysqlrecon.get_last_resp()

    ####
    # OsVersion
    if info['IsSysAdmin']:
        query = "DECLARE @ProductName  SYSNAME\n" \
                "EXECUTE master.dbo.xp_regread\n" \
                "@rootkey		= N'HKEY_LOCAL_MACHINE',\n" \
                "@key			= N'SOFTWARE\Microsoft\Windows NT\CurrentVersion',\n" \
                "@value_name		= N'ProductName',\n" \
                "@value			= @ProductName output\n" \
                "SELECT @ProductName;"
        pysqlrecon.query_handler(query)
        info['OsVersion'] = pysqlrecon.get_last_resp()

    ####
    # OsVersionNumber
    query = "SELECT RIGHT(SUBSTRING(@@VERSION, CHARINDEX('Windows Server', @@VERSION), 19), 4);"
    pysqlrecon.query_handler(query)
    info['OsVersionNumber'] = pysqlrecon.get_last_resp()

    ####
    # CurrentLogin
    pysqlrecon.query_handler("SELECT SYSTEM_USER;")
    info['CurrentLogin'] = pysqlrecon.get_last_resp()

    ####
    # ActiveSessions
    query = "SELECT COUNT(*) FROM [sys].[dm_exec_sessions] WHERE status = 'running';"
    pysqlrecon.query_handler(query)
    info['ActiveSessions'] = pysqlrecon.get_last_resp()

    # display results
    print()
    for key, val in info.items():
        key += ':'
        console.print(f"{' |->':>15} {key:25} {val}")
    print()

    pysqlrecon.disconnect()
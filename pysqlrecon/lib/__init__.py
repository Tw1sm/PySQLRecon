from impacket import tds
from typing import Any
from rich.table import Table

from pysqlrecon.lib.exceptions import DuplicateAssemblyError
from pysqlrecon.logger import logger, console
from pysqlrecon.lib.sqlagent import SqlAgentMixin
from pysqlrecon.lib.clr import ClrMixin
from pysqlrecon.lib.module import ModuleMixin
from pysqlrecon.lib.query import QueryMixin
from pysqlrecon.lib.sccm import SccmMixin


class PySqlRecon(SqlAgentMixin, ClrMixin, ModuleMixin, QueryMixin, SccmMixin):

    # https://learn.microsoft.com/en-us/sql/relational-databases/errors-events/database-engine-events-and-errors-6000-to-6999?view=sql-server-ver16
    DUPLICATE_ASM_ERROR = 6285


    def __init__(self, target, domain, username, password, port, link, impersonate,
                    db, hashes, aesKey, kerberos, no_pass, dc_ip, windows_auth) -> None:

        self.target = target
        self.domain = domain
        self.username = username
        self.password = password
        self.port = port
        self.link = link
        self.impersonate = impersonate
        self.db = db
        self.hashes = hashes
        self.aesKey = aesKey
        self.kerberos = kerberos
        self.dc_ip = dc_ip
        self.windows_auth = windows_auth

        self.ms_sql = None

        if self.password is None and self.username != '' and self.hashes is None and no_pass is False and self.aesKey is None:
            from getpass import getpass
            self.password = getpass("Password:")
            print()

    
    # connect to the SQL server
    def connect(self) -> None:
        logger.info(f"Connecting to {self.target}:{self.port}")
        self.ms_sql = tds.MSSQL(self.target, int(self.port))

        try:
            self.ms_sql.connect()
        except Exception as e:
            logger.error(str(e))
            exit()

        # if a link was specified, treat db name as remote db
        db = None if self.link is not None else self.db

        try:
            with console.status("Authenticating...", spinner="arc"):
                if self.kerberos is True:
                    logger.debug("Using Kerberos authentication")
                    self.ms_sql.kerberosLogin(db, self.username, self.password, self.domain, 
                                            self.hashes, self.aesKey, kdcHost=self.dc_ip)
                else:
                    self.ms_sql.login(db, self.username, self.password, self.domain, self.hashes, self.windows_auth)
        except Exception as e:
            logger.error(str(e))
            exit()

        self.print_replies()
        logger.debug("Login successful")

    
    # used to create a second connect for ADSI credential capture
    def make_dup_connection(self) -> None:
        logger.info(f"Initiating second connection to {self.target}:{self.port}")
        ms_sql = tds.MSSQL(self.target, int(self.port))
        ms_sql.connect()

        # if a link was specified, treat db name as remote db
        db = None if self.link is not None else self.db

        try:
            with console.status("Authenticating...", spinner="arc"):
                if self.kerberos is True:
                    logger.debug("Using Kerberos authentication")
                    ms_sql.kerberosLogin(db, self.username, self.password, self.domain, 
                                            self.hashes, self.aesKey, kdcHost=self.dc_ip)
                else:
                    ms_sql.login(db, self.username, self.password, self.domain, self.hashes, self.windows_auth)
        except Exception as e:
            logger.error(str(e))
            return None

        self.print_replies()
        logger.debug("Login successful")
        return ms_sql


    # disconnect from the SQL server
    def disconnect(self) -> None:
        self.ms_sql.disconnect()
        logger.debug("Disconnected from SQL server")

    
    # return value from single row/col queries
    # (i.e. SELECT @@VERSION)
    def get_last_resp(self, attr="") -> Any:
        return self.ms_sql.rows[0][attr]
    

    # ensure the specified linked server exists
    def validate_link(self, target_link=None, use_link=False) -> bool:
        query = "SELECT name FROM sys.servers WHERE is_linked = 1;"
        
        if use_link:
            self.exec_lquery(query)
        else:
            self.exec_standard_query("SELECT name FROM sys.servers WHERE is_linked = 1;")
        
        target_link = target_link.lower() if target_link is not None else self.link.lower()

        if target_link in [row['name'].lower() for row in self.ms_sql.rows]:
            return True
        
        return False



    # ensure the specified login can be impersonated
    def validate_impersonate(self) -> None:
        self.ms_sql.sql_query(
            "SELECT distinct b.name FROM sys.server_permissions a " \
            "INNER JOIN sys.server_principals b ON a.grantor_principal_id " \
            "= b.principal_id WHERE a.permission_name = 'IMPERSONATE';"
        )

        if self.impersonate.lower() not in [row['name'].lower() for row in self.ms_sql.rows]:
            logger.warning(f"The {self.impersonate} login cannot be impersonated")
            self.disconnect()
            exit()


    @staticmethod
    def validate_opts(link_compat, impersonate_compat, link, impersonate) -> bool:
        if link_compat is False and link is not None:
            logger.error("This command does not support links")
            return False

        if impersonate_compat is False and impersonate is not None:
            logger.error("This command does not support impersonation")
            return False

        return True
    

    def print_results(self, use_basic_tables) -> None:
        if len(self.ms_sql.rows) == 0:
            logger.warning("No results found")
            return
        
        # for xpcmdshell output
        #  replace blank lines that are reutned as 'NULL'
        if 'output' in self.ms_sql.rows[0]:
            for item in self.ms_sql.rows:
                for k, v in item.items():
                    if v == 'NULL':
                        item[k] = ''
        
        if use_basic_tables:
            self.print_basic_table()
        else:
            self.pretty_print_table()

    

    def print_basic_table(self) -> None:
        headers = ' | '.join(self.ms_sql.rows[0].keys())

        print()
        print(headers)
        print('-' * len(headers))

        for row in self.ms_sql.rows:
            print(' | '.join([str(value) for value in row.values()]))   

        print() 


    # format query results in Rich table
    def pretty_print_table(self) -> None:
        table = Table(
            row_styles=["none", "dim"]
        )
        
        # prep col headers
        for col in self.ms_sql.rows[0].keys():
            table.add_column(col, justify="left")

        for row in self.ms_sql.rows:
            table.add_row(*[value.decode('utf-8') if isinstance(value, bytes) else str(value) for value in row.values()])

        print()
        console.print(table)
        print()


    # https://github.com/fortra/impacket/blob/master/impacket/tds.py#L1019C5-L1051C8
    def print_replies(self) -> None:
        for keys in list(self.ms_sql.replies.keys()):
            for i, key in enumerate(self.ms_sql.replies[keys]):
                if key['TokenType'] == tds.TDS_ERROR_TOKEN:
                    error_num = key['Number']
                    error =  "(%s): Line %d: %s" % (key['ServerName'].decode('utf-16le'), key['LineNumber'], key['MsgText'].decode('utf-16le'))                                      
                    self.lastError = tds.SQLErrorException("ERROR: Line %d: %s" % (key['LineNumber'], key['MsgText'].decode('utf-16le')))
                    logger.error(error)

                    # handle duplicate assembly error
                    if error_num == PySqlRecon.DUPLICATE_ASM_ERROR:
                        raise DuplicateAssemblyError(error)
                    
                    exit()

                elif key['TokenType'] == tds.TDS_INFO_TOKEN:
                    logger.debug("(%s): Line %d: %s" % (key['ServerName'].decode('utf-16le'), key['LineNumber'], key['MsgText'].decode('utf-16le')))

                elif key['TokenType'] == tds.TDS_LOGINACK_TOKEN:
                    logger.debug("ACK: Result: %s - %s (%d%d %d%d) " % (key['Interface'], key['ProgName'].decode('utf-16le'), key['MajorVer'], key['MinorVer'], key['BuildNumHi'], key['BuildNumLow']))

                elif key['TokenType'] == tds.TDS_ENVCHANGE_TOKEN:
                    if key['Type'] in (tds.TDS_ENVCHANGE_DATABASE, tds.TDS_ENVCHANGE_LANGUAGE, tds.TDS_ENVCHANGE_CHARSET, tds.TDS_ENVCHANGE_PACKETSIZE):
                        record = tds.TDS_ENVCHANGE_VARCHAR(key['Data'])
                        if record['OldValue'] == '':
                            record['OldValue'] = 'None'.encode('utf-16le')
                        elif record['NewValue'] == '':
                            record['NewValue'] = 'None'.encode('utf-16le')
                        if key['Type'] == tds.TDS_ENVCHANGE_DATABASE:
                            _type = 'DATABASE'
                        elif key['Type'] == tds.TDS_ENVCHANGE_LANGUAGE:
                            _type = 'LANGUAGE'
                        elif key['Type'] == tds.TDS_ENVCHANGE_CHARSET:
                            _type = 'CHARSET'
                        elif key['Type'] == tds.TDS_ENVCHANGE_PACKETSIZE:
                            _type = 'PACKETSIZE'
                        else:
                            _type = "%d" % key['Type']                 
                        logger.debug("ENVCHANGE(%s): Old Value: %s, New Value: %s" % (_type,record['OldValue'].decode('utf-16le'), record['NewValue'].decode('utf-16le')))
       
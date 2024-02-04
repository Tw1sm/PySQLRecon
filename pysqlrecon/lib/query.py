from pysqlrecon.logger import logger


class QueryMixin:

    # basic query handler for simple commands like
    #  whoami, databases, columns, users, etc.
    def query_handler(self, query, use_rpc_query=False) -> None:
        try:
            # execute linked query
            if self.link is not None:
                if use_rpc_query and self.check_rpc_on_link(self.link):
                    self.exec_lquery_rpc(query)
                else:
                    self.exec_lquery(query)

            # execute impersonation query
            elif self.impersonate is not None:
                self.exec_iquery(query)

             # otherwise, exec standard query
            else:
                self.ms_sql.sql_query(query)

            self.print_replies()
        except Exception as e:
            logger.error(str(e))
            logger.error("Error executing query... Exiting")
            self.disconnect()
            exit()


    # execute standard SQL query
    def exec_standard_query(self, query) -> None:
        if self.impersonate is not None:
            self.exec_iquery(query)
        else:
            self.ms_sql.sql_query(query)
        self.print_replies()
    

    # execute impersonation query
    def exec_iquery(self, query) -> None:
        logger.debug(f"Impersonating {self.impersonate} for query")
        query = f"EXECUTE AS LOGIN = '{self.impersonate}'; " + query
        self.ms_sql.sql_query(query)
        self.print_replies()
    

    # execute linked query
    def exec_lquery(self, query) -> None:
        query = query.replace("'", "''")
        #print(f"SELECT * FROM OPENQUERY(\"{self.link}\", '{query}')")
        self.ms_sql.sql_query(
            f"SELECT * FROM OPENQUERY(\"{self.link}\", '{query}')"
        )
        self.print_replies()


    # check if rcp is enabled on the linked server
    def check_rpc_on_link(self, link) -> bool:
        query = f"SELECT is_rpc_out_enabled FROM sys.servers WHERE lower(name) like '%{link.lower()}%';"
        self.exec_standard_query(query)
        
        if self.ms_sql.rows[0]['is_rpc_out_enabled'] == 0:
            return False
        
        return True
    

    # execute a query against a linked SQL server using 'EXECUTE (QUERY) AT HOSTNAME
    def exec_lquery_rpc(self, query) -> None:
        query = query.replace("'", "''")
        query = f"EXECUTE ('{query}') AT {self.link};"
        self.ms_sql.sql_query(query)
        self.print_replies()

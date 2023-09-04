
class ClrMixin:

    # check if trusted assembly already exists
    def check_asm_hash(self, hash) -> bool:
        query = f"SELECT * FROM sys.trusted_assemblies where hash = 0x{hash};"

        if self.link is not None:
            self.exec_lquery(query)
        else:
            self.exec_standard_query(query)
        
        if hash.encode() in [row['hash'] for row in self.ms_sql.rows]:
            return True
        
        return False


    # add trusted assembly to SQL server
    def add_trusted_asm(self, dll_path, hash) -> None:
        query =  f"EXEC sp_add_trusted_assembly 0x{hash},N'{dll_path}" \
                  ", version=0.0.0.0, culture=neutral, publickeytoken=null, processorarchitecture=msil';"
        
        if self.link is not None:
            self.exec_lquery_rpc(query)
        else:
            self.exec_standard_query(query)


    # delete procedure and assembly associated with trusted assembly
    def delete_tasm_resources(self, asm_name, function, is_function=False) -> None:
        if is_function:
            drop_proc = f"DROP FUNCTION IF EXISTS {function};"
        else:
            drop_proc = f"DROP PROCEDURE IF EXISTS {function};"
        drop_asm = f"DROP ASSEMBLY IF EXISTS {asm_name};"

        if self.link is not None:
            self.exec_lquery_rpc(drop_proc)
            self.exec_lquery_rpc(drop_asm)
        else:
            self.exec_standard_query(drop_proc)
            self.exec_standard_query(drop_asm)


    # delete a trusted assembly on SHA-512 hash
    def delete_tasm(self, hash) -> None:
        query = f"EXEC sp_drop_trusted_assembly 0x{hash};"

        if self.link is not None:
            self.exec_lquery_rpc(query)
        else:
            self.exec_standard_query(query)


    # check if an assembly already exists
    def check_assembly(self, asm_name) -> bool:
        query = f"SELECT * FROM sys.assemblies where name = '{asm_name}';"

        if self.link is not None:
            self.exec_lquery(query)
        else:
            self.exec_standard_query(query)

        if asm_name in [row['name'] for row in self.ms_sql.rows]:
            return True
        
        return False


    # create new custom assembly
    def create_asm(self, asm_name, dll_bytes) -> None:
        query = f"CREATE ASSEMBLY {asm_name} FROM 0x{dll_bytes} WITH PERMISSION_SET = UNSAFE;"

        if self.link is not None:
            self.exec_lquery_rpc(query)
        else:
            self.exec_standard_query(query)


    # check if a stored procedure already exists
    def check_asm_sp(self, function) -> bool:
        query = "SELECT SCHEMA_NAME(schema_id), name FROM sys.procedures WHERE type = 'PC';"

        if self.link is not None:
            self.exec_lquery(query)
        else:
            self.exec_standard_query(query)

        if function in [row['name'] for row in self.ms_sql.rows]:
            return True
        
        return False
    

    # check if a function already exists
    def check_asm_func(self, function) -> bool:
        query = "SELECT * FROM sys.assembly_modules;"

        if self.link is not None:
            self.exec_lquery(query)
        else:
            self.exec_standard_query(query)

        if function in [row['assembly_class'] for row in self.ms_sql.rows]:
            return True

        return False


    # create stored procedure for custom assembly
    def create_asm_sp(self, asm_name, function, procedure=None) -> None:
        if procedure is None:
            query = f"CREATE PROCEDURE [dbo].[{function}]" \
                    f"AS EXTERNAL NAME [{asm_name}].[StoredProcedures].[{function}]"
        else:
            query = procedure
        
        if self.link is not None:
            self.exec_lquery_rpc(query)
        else:
            # need to break out of normal impersonation workflow here
            if not self.impersonate:
                self.exec_standard_query(query)
            else:
                self.ms_sql.sql_query(f"EXECUTE AS LOGIN = '{self.impersonate}';")
                self.print_replies()
                self.ms_sql.sql_query(query)
                self.print_replies()


    # execute functuon for custom assembly
    def exec_asm_sp(self, function) -> None:
        query = f"EXEC {function}"

        if self.link is not None:
            self.exec_lquery_rpc(query)
        else:
            self.exec_standard_query(query)
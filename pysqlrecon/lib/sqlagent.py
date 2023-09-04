import random
import string

from pysqlrecon.logger import logger


class SqlAgentMixin:
    
    # get SQL agent status
    def get_agent_status(self) -> bool:
        query = "SELECT dss.[status], dss.[status_desc] FROM sys.dm_server_services dss \n" \
            "WHERE dss.[servicename] LIKE 'SQL Server Agent (%';"
    
        if self.link is not None:
            self.exec_lquery(query)
        else:
            self.exec_standard_query(query)

        if "running" not in self.get_last_resp("status_desc").lower():
            return False
        
        return True
        

    # get SQL agent jobs
    def get_agent_jobs(self) -> None:
        query = "SELECT job_id, name, enabled, date_created, date_modified\n" \
            "FROM msdb.dbo.sysjobs ORDER BY date_created"
        
        if self.link is not None:
            self.exec_lquery(query)
        else:
            self.exec_standard_query(query)
    

    # run a command via SQL agent jobs
    def add_agent_job(self, cmd, job_name=None, step_name=None) -> str:
        if job_name is None:
            job_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) 
        
        if step_name is None:
            step_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        logger.info(f"Setting job_name to '{job_name}'")
        logger.info(f"Setting step_name to '{step_name}'")

        query = "use msdb;\n" \
            f"EXEC dbo.sp_add_job @job_name = '{job_name}';\n" \
            f"EXEC sp_add_jobstep @job_name = '{job_name}', \n" \
            f"@step_name = '{step_name}', \n" \
            "@subsystem = 'PowerShell', \n" \
            f"@command = '{cmd}', \n" \
            "@retry_attempts = 1, \n" \
            "@retry_interval = 5;\n" \
            f"EXEC dbo.sp_add_jobserver @job_name = '{job_name}';"
        
        if self.link is not None:
            self.exec_lquery_rpc(query)
        else:
            self.exec_standard_query(query)

        return job_name
    

    # run a SQL agent job
    def exec_agent_job(self, job_name) -> None:
        query = "use msdb;" \
                f"EXEC dbo.sp_start_job '{job_name}';" \
                "WAITFOR DELAY '00:00:05';"
        
        if self.link is not None:
            self.exec_lquery_rpc(query)
        else:
            self.exec_standard_query(query)


    # delete a SQL agent job
    def delete_agent_job(self, job_name) -> None:
        query = "use msdb;\n" \
                f"EXEC dbo.sp_delete_job  @job_name = '{job_name}';"
        
        if self.link is not None:
            self.exec_lquery_rpc(query)
        else:
            self.exec_standard_query(query)
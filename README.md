<h1 align="center">
<img height=250 src=resources/images/snake_logo.png />

PySQLRecon

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PyPi](https://img.shields.io/pypi/v/pysqlrecon?style=for-the-badge)
</h1>

PySQLRecon is a Python port of the awesome [SQLRecon](https://github.com/skahwah/SQLRecon) project by [@sanjivkawa](https://twitter.com/sanjivkawa). See the [commands](#commands) section for a list of capabilities.

## Install
PySQLRecon can be installed with `pip3 install pysqlrecon` or by cloning this repository and running `pip3 install .`

## Commands
All of the main modules from SQLRecon have equivalent commands. Commands noted with `[PRIV]` require elevated privileges or sysadmin rights to run. Alternatively, commands marked with `[NORM]` can likely be run by normal users and do not require elevated privileges. 

Support for impersonation (`[I]`) or execution on linked servers (`[L]`) are denoted at the end of the command description.

```
adsi                 [PRIV] Obtain ADSI creds from ADSI linked server [I,L]
agentcmd             [PRIV] Execute a system command using agent jobs [I,L]
agentstatus          [PRIV] Enumerate SQL agent status and jobs [I,L]
checkrpc             [NORM] Enumerate RPC status of linked servers [I,L]
clr                  [PRIV] Load and execute .NET assembly in a stored procedure [I,L]
columns              [NORM] Enumerate columns within a table [I,L]
databases            [NORM] Enumerate databases on a server [I,L]
disableclr           [PRIV] Disable CLR integration [I,L]
disableole           [PRIV] Disable OLE automation procedures [I,L]
disablerpc           [PRIV] Disable RPC and RPC Out on linked server [I]
disablexp            [PRIV] Disable xp_cmdshell [I,L]
enableclr            [PRIV] Enable CLR integration [I,L]
enableole            [PRIV] Enable OLE automation procedures [I,L]
enablerpc            [PRIV] Enable RPC and RPC Out on linked server [I]
enablexp             [PRIV] Enable xp_cmdshell [I,L]
impersonate          [NORM] Enumerate users that can be impersonated
info                 [NORM] Gather information about the SQL server
links                [NORM] Enumerate linked servers [I,L]
olecmd               [PRIV] Execute a system command using OLE automation procedures [I,L]
query                [NORM] Execute a custom SQL query [I,L]
rows                 [NORM] Get the count of rows in a table [I,L]
search               [NORM] Search a table for a column name [I,L]
smb                  [NORM] Coerce NetNTLM auth via xp_dirtree [I,L]
tables               [NORM] Enumerate tables within a database [I,L]
users                [NORM] Enumerate users with database access [I,L]
whoami               [NORM] Gather logged in user, mapped user and roles [I,L]
xpcmd                [PRIV] Execute a system command using xp_cmdshell [I,L]     
```

## Usage
PySQLRecon has global options (available to any command), with some commands introducing additional flags. All global options must be specified *before* the command name:
```
pysqlrecon [GLOBAL_OPTS] COMMAND [COMMAND_OPTS]
```

View global options:
```
pysqlreocn --help
```

View command specific options:
```
pysqlrecon [GLOBAL_OPTS] COMMAND --help
```

Change the database authenticated to, or used in certain PySQLRecon commands (`query`, `tables`, `columns` `rows`), with the `--database` flag.

Target execution of a PySQLRecon command on a linked server (instead of the SQL server being authenticated to) using the `--link` flag.

Impersonate a user account while running a PySQLRecon command with the `--impersonate` flag.

`--link` and `--impersonate` and not compatible when used together.


## Development
pysqlrecon uses Poetry to manage dependencies. Install from source and setup for development with:
```
git clone https://github.com/tw1sm/pysqlrecon
cd pysqlrecon
poetry install
poetry run pysqlrecon --help
```

### Adding a Command
PySQLRecon is easily extensible - see the template and instructions in [resources](resources/command_template/)

## References and Credits
- [Impacket](https://github.com/fortra/impacket)
- [@sanjivkawa](https://twitter.com/sanjivkawa) for the [SQLRecon](https://github.com/skahwah/SQLRecon) project
- [https://securityintelligence.com/x-force/databases-beware-abusing-microsoft-sql-server-with-sqlrecon/](https://securityintelligence.com/x-force/databases-beware-abusing-microsoft-sql-server-with-sqlrecon/)
- [https://gist.github.com/skahwah/a585e176e4a5cf319b0c759637f5c410](https://gist.github.com/skahwah/a585e176e4a5cf319b0c759637f5c410)
- Also checkout [MSSqlPwner](https://github.com/ScorpionesLabs/MSSqlPwner) for other offensive MSSQL capabilities written in Python

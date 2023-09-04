## Adding a custom command
1. Copy the `command.py` template into `pysqlrecon/modules/`
2. Customize the module
    - Add your commands logic and CLI options
    - Determine if elevated DB privs are required for use
    - Set support for linked servers and impersonation
3. Import the command into `pysqlrecon/modules/__init__.py` and add it to the `__all__` list
4. Verify that the new command exists with `pysqlrecon --help`
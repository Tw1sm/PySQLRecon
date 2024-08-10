import typer

from pysqlrecon.modules.sccm import users, sites, credentials, logons, tasklist, taskdata, \
                                    addadmin, removeadmin

__all__ = [
    addadmin,
    credentials,
    logons,
    removeadmin,
    sites,
    taskdata,
    tasklist,
    users
]

COMMAND_NAME = "sccm"
HELP = "[blue][SUBM][/] Submodule for SCCM specific commands"


app = typer.Typer(add_completion=False,
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


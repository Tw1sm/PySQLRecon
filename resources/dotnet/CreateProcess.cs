using System;
using System.Data.SqlClient;
using System.Data.SqlTypes;
using System.Diagnostics;
using System.Runtime.InteropServices;
using Microsoft.SqlServer.Server;

public partial class StoredProcedures
{       
    [Microsoft.SqlServer.Server.SqlProcedure]
    public static void CreateProcess ()
    {
        Process.Start("notepad.exe");
    }
}

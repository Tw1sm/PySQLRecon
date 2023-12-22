import re


class DuplicateAssemblyError(Exception):
    """
    Exception raised for creation of a CLR assembly that already exsists
    """
    
    def __init__(self, message):
        self.assembly_name = ""

        # extract the name of the assembly from the message       
        match = re.search(r'name "(.*?)"', message)
        if match:
            self.assembly_name = match.group(1)
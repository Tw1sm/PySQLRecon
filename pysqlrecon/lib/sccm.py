from Crypto.Cipher import DES3
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1
from Crypto.Util.Padding import unpad
import struct

from pysqlrecon.logger import logger


class SccmMixin:
    
    def handle_taskdata(self):
        if len(self.ms_sql.rows) == 0:
            logger.warning("No results found")
            return
        
        #
        # Expecting PkgID | Name | Sequence
        # 
        for row in self.ms_sql.rows:
            print(f"Task Sequence: {row['Name']}")
            print(f"{'-' * 15}")
            print(row['Sequence'])
            print()

        # convert hexs to bytes
        seq = row['Sequence']
        data = self.decode_data(seq)
        print(data)
    

    @staticmethod
    def convert_sid_to_binary(sid_string):
        # Split the SID string into its components
        sid_parts = sid_string.split('-')
        
        # Extract the revision level (first part after 'S')
        revision = int(sid_parts[1])
        
        # Extract the identifier authority (next part)
        identifier_authority = int(sid_parts[2])
        
        # Extract the sub authorities (remaining parts)
        sub_authorities = [int(part) for part in sid_parts[3:]]

        # Create the binary representation
        # Start with revision and sub-authority count
        sid_binary = struct.pack('B', revision) + struct.pack('B', len(sub_authorities))
        
        # Handle identifier authority
        if identifier_authority > 0xFFFFFFFF:
            sid_binary += struct.pack('>Q', identifier_authority)[2:]
        else:
            sid_binary += b'\x00\x00' + struct.pack('>I', identifier_authority)

        # Add each sub authority
        for sub_authority in sub_authorities:
            sid_binary += struct.pack('<I', sub_authority)

        return sid_binary


from Crypto.Cipher import DES3
from hashlib import sha1
import struct

from pysqlrecon.logger import logger


class SccmMixin:

    #
    # https://github.com/skahwah/SQLRecon/blob/main/SQLRecon/SQLRecon/modules/SCCM.cs#L844
    #
    @staticmethod
    def decode_data(encrypted_blob):

        data_len = struct.unpack_from('<I', encrypted_blob, 52)[0]
        encrypted_data = encrypted_blob[64:64 + data_len]
        logger.debug(f"Encrypted data length: {data_len}")

        hash_base = encrypted_blob[4:44]

        logger.debug(f"Hash Base: [ {', '.join([str(byte) for byte in hash_base])} ]")

        key = SccmMixin.aes_des_key_derivation(hash_base)[:24]
        logger.debug(f"Derived Key: [ {', '.join([str(byte) for byte in key])} ]")
        
        iv = bytes([0] * 8)
        cipher = DES3.new(key, DES3.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_data)

        # Remove PKCS7 padding
        padding_len = decrypted[-1]
        if isinstance(padding_len, int) and padding_len > 0 and padding_len <= 8:
            decrypted = decrypted[:-padding_len]

        try:
            decoded_string = decrypted.decode('utf-16-le')
        except UnicodeDecodeError as e:
            print(f"Decoding error: {e}")
            raise

        return decoded_string
    

    #
    # https://github.com/MWR-CyberSec/PXEThief/blob/main/media_variable_file_cryptography.py#L23
    #
    @staticmethod
    def aes_des_key_derivation(password):
        key_sha1 = sha1(password).digest()
        
        b0 = b""
        for x in key_sha1:
            b0 += bytes((x ^ 0x36,))
            
        b1 = b""
        for x in key_sha1:
            b1 += bytes((x ^ 0x5c,))

        # pad remaining bytes with the appropriate value
        b0 += b"\x36"*(64 - len(b0))
        b1 += b"\x5c"*(64 - len(b1))
            
        b0_sha1 = sha1(b0).digest()
        b1_sha1 = sha1(b1).digest()
        
        return b0_sha1 + b1_sha1
    

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


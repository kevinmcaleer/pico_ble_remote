# UUIDs

import bluetooth
import machine
import struct

_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_BUTTON = bluetooth.UUID(0x0000)


def _encode_message(character:str):
    """ Encode a message to send to the remote device """
    return struct.pack("<h", ord(character))

def _decode_message(message:bytes):
    """ Decode a message received from the remote device """
    return struct.unpack("<h", message)[0]


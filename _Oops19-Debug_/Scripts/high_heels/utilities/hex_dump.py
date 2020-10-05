#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#



class HexDump:
    def __init__(self):
        self.memory_address = 0
        self.hex_string = ""
        self.ascii_string = ""
        self.buffer = ""
        self.result = []

    def _is_printable_ascii_character(self, i: int) -> bool:
        """
        :param i: The code point of the character, e.g. ord('A') or ord('€')
        :return: Returns true if the character is a 7 bit ASCII or one-byte UTF-8 printable character
        """
        return (i > 31) and (i < 127)

    def _convert_to_printable_character(self, i: int, replacement_character: str = '.') -> int:
        """
        :param i: The code point of the character, e.g. ord('A') or ord('€')
        :param replacement_character: Non-printable characters will be replaced by this character.
        :param transliteration: Non ASCII characters may be translated to ASCII (ê to e). Useful information gets lost but this may be better than a '.'. 'unidecode' has to be installed.
        :return: The character code point as is, a transliterated character code point or the code point of the replacement_character if the character can not be printed.
        """
        rv = i
        if not self._is_printable_ascii_character(i):
            rv = ord(replacement_character)
        return rv

    def _process_byte(self, i):
        self.ascii_string = self.ascii_string + chr(self._convert_to_printable_character(i))
        if self.memory_address % 16 == 0:
            self.result.append(f"{self.buffer}")
            self.buffer = f"{self.memory_address:06X} {i:02X}"
        elif self.memory_address % 16 == 15:
            self.buffer = f"{self.buffer} {i:02X} {self.ascii_string}"
            self.ascii_string = ""
            self.hex_string = ""
        else:
            self.buffer = f"{self.buffer} {i:02X}"
        self.memory_address = self.memory_address + 1

    def process_stream(self, resource, read_n_bytes: int = 128) -> str:
        """
        :param resource:  A stream to read data from
        :param read_n_bytes: The number of bytes to read and to convert hex.
        :return: String with hex dump of read data
        """
        b = resource.read(1)
        read_bytes = 1
        while b:
            i: int = int.from_bytes(b, byteorder='big')  # convert to int - reading byte-wise the value will never be > 255.
            self._process_byte(i)
            if read_bytes >= read_n_bytes:
                break
            b = resource.read(1)
            read_bytes = read_bytes + 1
        self.result.append(f"{self.buffer}")

        return self.result


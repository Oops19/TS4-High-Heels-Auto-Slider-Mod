#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#


class FNV:
    '''
    Simple class to generate Fowler-Noll-Vo (FNV) values.
    The Sims 4 (TS4) uses FNV a lot and it may com in handy to have a python class to calculate it.
    It supports UCS-2 and UTF-8, conversion to lower case and setting the high bit.
    Only FNV24, FNV32, FNV56 and FNV64 are and will be supported in future.
    '''
    fnv_primes = {32: 16777619, 64: 1099511628211}
    # fnv_hashes = {32: 0x811C9DC5, 64: 0xCBF29CE484222325} - these will be calculated on-the-fly
    FNV_BYTES = "chongo <Landon Curt Noll> /\\../\\".encode(encoding='utf-8')  # ASCII to UTF-8 will be ASCII after conversion ;)
    FNV_HASH = 0

    @staticmethod
    def _fnv_UTF8(bytes, hash_value, prime, max_size):
        for b in bytes:
            hash_value = (hash_value * prime) % max_size
            hash_value = hash_value ^ b
        return hash_value

    @staticmethod
    def _fnv_UTF16(words, hash_value, prime, max_size):
        for i in range(0, len(words), 2):
            print(".")
            w = words[i] << 8 | words[i+1]
            hash_value = (hash_value * prime) % max_size
            hash_value = hash_value ^ w
        return hash_value

    @classmethod
    def get(cls, text: str, n: int, ascii_2_lower: bool = False, ucs2: bool = False, set_high_bit: bool = False):
        '''
        For TS4 set utf16=True and ascii_2_lower=True and often also set_high_bit=True
        :param text: The string to get the FNV value for.
        :param n: The exponent for the size of the FNV value (2^n) - 24, 32 and 56, 64 are supported. (56 is used for i18n in TS4)
        :param ascii_2_lower: ASCII characters in strings may be converted to lower case. If enabled fnv('A') = fnv('a'). TS4 requires this.
        :param ucs2: Strings are converted to UTF8 (=False) or UCS-2 (=True) bytes to calculate the hash
        :param set_high_bit: Set the high bit. This is recommended for FNV values in TS4 mods.
        :return: The fnv value or 0
        '''
        hash_value = 0
        m = None
        if (n == 24) or (n == 32):
            m = 32
        elif (n == 56) or (n == 64):
            m = 64
        if m:
            max_size = 2 ** m
            prime = cls.fnv_primes.get(m)
            hash_value = cls._fnv_UTF8(cls.FNV_BYTES, cls.FNV_HASH, prime, max_size)

            if ascii_2_lower:
                text = text.lower()

            if ucs2:
                # € as UCS-2: 0x20AC
                _words = text.encode(encoding='utf-16be')
                hash_value = cls._fnv_UTF16(_words, hash_value, prime, max_size)
            else:
                # € as UTF-8: 0xE2 0x82 0xAC
                _bytes = text.encode(encoding='utf-8')
                hash_value = cls._fnv_UTF8(_bytes, hash_value, prime, max_size)

            if n != m:
                hash_value = (hash_value >> n) ^ (hash_value & (1 << n) - 1)

            if set_high_bit:
                high_value = 1 << (m - 1)
                hash_value = hash_value | high_value

        return hash_value

#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#

# Simple code snippet to check the FNV implementation

import sims4.commands
import sims4
import sims4.hash_util
from high_heels.utilities.fnv import FNV

ascii_2_lower = True  # Enforce .lower() for TS4
ucs2 = True  # Set UCS-2 to True for TS4


def get_all(text: str = '') -> []:
    global ascii_2_lower, ucs2
    fnv = FNV()
    x64 = fnv.get(text, 64, ascii_2_lower=ascii_2_lower, ucs2=ucs2)
    h64 = fnv.get(text, 64, ascii_2_lower=ascii_2_lower, ucs2=ucs2, set_high_bit=True)
    x56 = fnv.get(text, 56, ascii_2_lower=ascii_2_lower, ucs2=ucs2)
    h56 = fnv.get(text, 56, ascii_2_lower=ascii_2_lower, ucs2=ucs2, set_high_bit=True)
    x32 = fnv.get(text, 32, ascii_2_lower=ascii_2_lower, ucs2=ucs2)
    h32 = fnv.get(text, 32, ascii_2_lower=ascii_2_lower, ucs2=ucs2, set_high_bit=True)
    x24 = fnv.get(text, 24, ascii_2_lower=ascii_2_lower, ucs2=ucs2)
    h24 = fnv.get(text, 24, ascii_2_lower=ascii_2_lower, ucs2=ucs2, set_high_bit=True)

    ts4_32 = sims4.hash_util.hash32(text)
    ts4_64 = sims4.hash_util.hash64(text)

    return x64, h64, x56, h56, x32, h32, x24, h24, ts4_32, ts4_64


@sims4.commands.Command('o19.fnv.ucs2', command_type=sims4.commands.CommandType.Live)
def o19_fnv(_connection=None):
    global ascii_2_lower, ucs2
    output = sims4.commands.CheatOutput(_connection)
    ucs2 = not ucs2
    output(f"UCS-2 is {ucs2}")


@sims4.commands.Command('o19.fnv.case', command_type=sims4.commands.CommandType.Live)
def o19_fnv(_connection=None):
    global ascii_2_lower, ucs2
    output = sims4.commands.CheatOutput(_connection)
    ascii_2_lower = not ascii_2_lower
    output(f"to_lower = {ascii_2_lower}")


@sims4.commands.Command('o19.fnv', command_type=sims4.commands.CommandType.Live)
def o19_fnv(text='', _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        x64, h64, x56, h56, x32, h32, x24, h24, ts4_32, ts4_64 = get_all(text)
        output(f"\nText: {text}")
        output(f"o19.fnv.ucs2 is {ucs2}")
        output(f"o19.fnv.case is {ascii_2_lower}")
        # A mess with TABs, change the output to a fixed width font to avoid this.
        output(f"fnvMM:\t_hex_Normal_\t\t\t_hex_HighBit_\t\t\t_dec_Normal_\t\t\t_dec_HighBit_")
        output(f"FNV24:\t0x{x24:08X}\t\t\t0x{h24:08X}\t\t\t{x24:10}\t\t\t{h24:10}")
        output(f"FNV32:\t0x{x32:08X}\t\t\t0x{h32:08X}\t\t\t{x32:10}\t\t\t{h32:10}")
        output(f"TS4:\t\t0x{ts4_32:08X}\t\t\t\t\t\t\t\t{ts4_32:10}")
        # True fnv56 - for locales usually fnv64 is used with the first word replaced with '00', ., 'FF'
        output(f"FNV56:\t0x{x56:016X}\t0x{h56:016X}\t{x56:20}\t{h56:20}")
        output(f"FNV64:\t0x{x64:016X}\t0x{h64:016X}\t{x64:20}\t{h64:20}")
        output(f"TS4:\t\t0x{ts4_64:016X}\t\t\t\t\t\t{ts4_64:20}")

        # Fixed width output
        # output(get_unicode_full_width(f"FNV24: 0x{x24:08X} 0x{h24:08X} {x24:10} {h24:10}"))
        # output(get_unicode_full_width(f"FNV32: 0x{x32:08X} 0x{h32:08X} {x32:10} {h32:10}"))
        # output(get_unicode_full_width(f"TS4:   0x{ts4_32:08X}            {ts4_32:10}"))
        # Console output too small :(
        # output(get_unicode_full_width(f"FNV56: 0x{x56:016X} 0x{h56:016X} {x56:20} {h56:20}"))
        # output(get_unicode_full_width(f"FNV64: 0x{x64:016X} 0x{h64:016X} {x64:20} {h64:20}"))
        # output(get_unicode_full_width(f"TS4:   0x{ts4_64:016X}                    {ts4_64:20}"))
    except:
        pass


def get_unicode_full_width(text: str = '') -> str:
    '''
    Convert an ASCII text string to full-width unicode characters.
    Simplest code, not for production.
    :param text:
    :return:
    '''
    # http://xahlee.info/comp/unicode_full-width_chars.html
    # to be completed ...
    translate = {
        'T': u'\uff34',
        'S': u'\uff33',
        ' ': u'\u3000',
        # 'F': u'\uff26"',
        'N': u'\uff2e',
        'V': u'\uff36',
        ':': u'\uff1a',
        'x': u'\uff58',
        '0': u'\uff10',
        '1': u'\uff11',
        '2': u'\uff12',
        '3': u'\uff13',
        '4': u'\uff14',
        '5': u'\uff15',
        '6': u'\uff16',
        '7': u'\uff17',
        '8': u'\uff18',
        '9': u'\uff19',
        'A': u'\uff21',
        'B': u'\uff22',
        'C': u'\uff23',
        'D': u'\uff24',
        'E': u'\uff25',
        'F': u'\uff26',
    }

    for k, v in translate.items():
        text = text.replace(k, v)
    return text



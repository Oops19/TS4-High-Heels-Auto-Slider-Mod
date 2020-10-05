#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
# Includes code from andrew https://sims4studio.com/thread/15145/started-python-scripting?page=4 and https://github.com/andrew-tavera/dbpf-reader-py
# License: Creative Commons Zero v1.0 Universal
# © andrew-tavera


# core/sims4/resources.py - CASPART = 55242443
# core/sims4/resources.py - CLIP_HEADER = 3158986820
'''
This class is still a mess in itself. Release early and often.
Nevertheless 'o19.res' is the command for the cheat console.
It is strongly recommended to remove all CC except the needed ones. Processing 10 GB of CC may crash the game.
To process mod data use 'o19.res.data'. Otherwise game data will be processed.
With 'o19.res.dump CASPART' data of all items will be written to the Mods folder - not to 'configuration' as intended.  TODO Fixme
'my_dump_test_2()' may be used in Python to format the output for the slider mod.

'''

import time
import sims4

from high_heels.utilities.hex_dump import HexDump
import fnmatch
import io
import os
import os.path
import struct
import zlib
import sims4.resources
import sims4.commands
import sims4.log
import paths
from typing import List, Iterator, Tuple, Callable, Set

output = None
dump_empty_packages = True  # Faster than parsing every item, if print_pretty = False
print_pretty = True  # Print pretty - one very long line may be hard to read
# r_type = sims4.resources.Types.CASPART
parse_mods = False  # Parse game data
do_hex_dump = 0  # Do not hex dump

#########################################################################################
#########################################################################################

def get_packages(folder: str, pattern: str = '*.package') -> Set[str]:
    packages: Set[str] = set()
    for root, dirs, files in os.walk(folder):
        for filename in fnmatch.filter(files, pattern):
            package_path = str(os.path.join(root, filename))
            packages.add(package_path)
    return packages


def get_name_CASPART(resource):
    text = ''
    # SKIP 0x02 Version
    # SKIP 0x02 TGI list (Type Group Index)
    # SKIP 0x02 presets
    resource.seek(0x0c, io.SEEK_SET)
    b = resource.read(1)  # 1 byte according to doc
    text_length: int = int.from_bytes(b, byteorder='big')

    b = resource.read(1)
    start_of_text: int = int.from_bytes(b, byteorder='big')
    if start_of_text == 0:
        resource.seek(0x0d, io.SEEK_SET)  # rewind 1 byte
    # else:
    #     '1' - consume this byte, do not rewind. Otherwise the output will be garbled.
    #     resource.seek(0x0e, io.SEEK_SET)

    # text = resource.read(text_length).decode("unicode") - not supported by python even though python uses unicode internally (2 bytes for each char)
    for i in range(text_length >> 1):  # == int(text_length-2)) as data is stored as Unicode (2 bytes for each char)
        b = resource.read(2)
        i: int = int.from_bytes(b, byteorder='big')
        text = f"{text}{chr(i)}"
    return text

def get_name_CLIP_HEADER(resource):
    # SKIP a lot of unknown things
    resource.seek(0x38, io.SEEK_SET)
    text_length: int = struct.unpack('i', resource.read(4))[0]
    text: str = resource.read(text_length).decode('ascii')
    return text

def get_name_HEX_DUMP(resource):
    try:
        hd = HexDump()
        text = hd.process_stream(resource)
        return f"{text}"
    except Exception as e:
        raise e

def read_package(filename: str, type_filter: set) -> Iterator[Tuple[int, int, int, Callable[[], bytes]]]:
    type_filter = set() if not type_filter else type_filter
    with open(filename, 'rb') as stream:
        def u32() -> int:
            return struct.unpack('I', stream.read(4))[0]

        # 1st bytes === 'DBPF' - .package file format
        # https://wiki.sc4devotion.com/index.php?title=DBPF
        # stream.seek(0, io.SEEK_SET) - not needed
        tag = stream.read(4).decode('ascii')
        assert tag == 'DBPF'

        stream.seek(32, io.SEEK_CUR)  # relative read to 36
        #stream.seek(36, io.SEEK_SET)  # 36 == pos of Index entry count
        index_entry_count = u32()
        stream.seek(24, io.SEEK_CUR)  # relative read to 64
        #stream.seek(64, io.SEEK_SET)  # 64 == pos of Index offset
        index_offset = u32()
        stream.seek(index_offset, io.SEEK_SET)  # Read the index
        index_flags: int = u32()
        # https://wiki.sc4devotion.com/index.php?title=DBPF_Source_Code
        # https://wiki.sc4devotion.com/images/9/94/DBPF_File_Format_v2.0.png
        # https://modthesims.info/archive/index.php?t-618074.html - {0x0000: "Uncompressed", 0xfffe: "Streamable compression", 0xffff: "Internal compression", 0xffe0: "Deleted record", 0x5a42: "ZLIB"}

        # 100% andrew, code is hard to understand but it works. Comments added by Oops19.
        # Read 'Entry Type' of TGI Block (Type Group Index)
        static_t: int = u32() if index_flags & 0x1 else 0
        static_g: int = u32() if index_flags & 0x2 else 0
        static_i: int = u32() << 32 if index_flags & 0x4 else 0
        static_i |= u32() if index_flags & 0x8 else 0

        for _ in range(index_entry_count):
            t = static_t if index_flags & 0x1 else u32()
            g = static_g if index_flags & 0x2 else u32()
            instance_hi = static_i >> 32 if index_flags & 0x4 else u32()
            instance_lo = static_i & 0xFFFFFFFF if index_flags & 0x8 else u32()
            i = (instance_hi << 32) + instance_lo                                   # Instance ID (?)
            offset: int = u32()                                                     # File location
            sz: int = u32()                                                         # File size (raw)
            file_size: int = sz & 0x7FFFFFFF                                        # strip high-bit(file size) ==> file size
            stream.seek(4, io.SEEK_CUR)                                             # File size (Decompressed) - do not read
            compressed: bool = sz & 0x80000000 > 0                                  # if high-bit(file size) ==> compressed
            compression_type: int = 0
            if compressed:
                compression_type = struct.unpack('H', stream.read(2))[0]            # Compression flag (0x0000==No, >0==Yes)
                stream.seek(2, io.SEEK_CUR)                                         # Unknown (0x0001)

            if compression_type not in (0x0000, 0x5A42):                            # Uncompressed, ZLIB
                continue

            def load_func() -> bytes:
                pos = stream.tell()                                                 # get current fp position
                stream.seek(offset, io.SEEK_SET)                                    # set to 'offset'
                data = stream.read(file_size)                                       # read the file
                stream.seek(pos, io.SEEK_SET)                                       # restore fp position
                return zlib.decompress(data) if compression_type == 0x5A42 else data

            if len(type_filter) == 0 or t in type_filter:
                yield t, g, i, load_func


def get_clips_from_package_v2(f, r_type, package) -> [dict, int]:
    global do_hex_dump
    id_2_res_name = dict()
    ids = set()
    failures: int = 0
    for t, g, i, load_func in read_package(package, type_filter={r_type}):
        try:
            with io.BytesIO(load_func()) as resource:
                res_name = ''
                if do_hex_dump:
                    res_name = get_name_HEX_DUMP(resource) ## TODO dump to log file
                    do_hex_dump = None
                elif r_type == sims4.resources.Types.CASPART:
                    res_name = get_name_CASPART(resource)
                elif r_type == sims4.resources.Types.CLIP_HEADER:
                    res_name = get_name_CLIP_HEADER(resource)
                id_2_res_name.update({i: res_name})
        except Exception as ex:
            f.write(f"get_clips_from_package_v2() Bad key: {g:x} {i:x} {t:x} in {package} ({ex}")
            failures += 1
        if do_hex_dump is None:
            break
    return id_2_res_name, failures

def get_clips_from_folder_v2(f, r_type, packages: Set[str]) -> Tuple[Set[str], int]:
    global do_hex_dump
    items = dict()
    failures: int = 0
    for package in packages:
        try:
            id_2_res_name, package_failures = get_clips_from_package_v2(f, r_type, package)
            ids: dict = items.get(package, dict())
            ids.update(id_2_res_name)
            items.update({package: ids})
            failures += package_failures
        except Exception as ex:
            failures += 1
            f.write(f"get_clips_from_folder_v2() Failed to read package {package} ({ex})")
        if do_hex_dump is None:
            do_hex_dump = True
            break
    return items, failures


@sims4.commands.Command('o19.res.dump', command_type=sims4.commands.CommandType.Live)
def debug_o19_dump(p_r_type = None, _connection=None):
    global max_file_size, dump_empty_packages, print_pretty
    output = sims4.commands.CheatOutput(_connection)
    try:
        try:
            from high_heels.utilities.helper_standalone import O19Helper
            oh = O19Helper(output)
        except:
            print_pretty = False
        #### TODO DUMP hexdump to a unique file !!!!
        # Add hexdump_counter for 2-3 dumps
        keys = set(item.name for item in sims4.resources.Types)
        if (p_r_type is None) or (p_r_type.upper() not in keys):
            output(f"[resource type]'{p_r_type}' missing or invalid")
            o19_hh_sliders_help(_connection)
            return
        r_type = sims4.resources.Types[p_r_type.upper()]  # methods and parameters will always be lower case

        # code starts here
        game_folder = os.path.dirname(os.path.dirname(os.path.dirname(paths.APP_ROOT)))
        mods_folder = os.path.expanduser(os.path.join('~', 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods'))
        if parse_mods:
            file_name = f'items.mods.{p_r_type}.txt'
            folder = mods_folder
            info_str = 'Mod'
        else:
            file_name = f'items.game.{p_r_type}.txt'
            folder = game_folder
            info_str = 'Game'
        file_name = os.path.join(mods_folder, file_name)
        log_file = os.path.join(mods_folder, f"{file_name}.log")

        # Gather all package file names
        packages = get_packages(folder)
        output(f"Processing {len(packages)} '{info_str}' packages. This may take some time (usually less than 1 second for 10000 items. Game packages contain many itesm.).")
        time.sleep(0.7)

        with open(log_file, 'w+') as f:
            items, failures = get_clips_from_folder_v2(f, r_type, packages)
            output(f'Found {len(items)}({failures}) items(errors).')

        output(f'Writing data to {file_name}.')

        if dump_empty_packages:
            with open(file_name, 'w+') as f:
                if print_pretty:
                    oh.print_pretty(f, f"{items}")
                else:
                    f.write(f"{items}")
        else:
            with open(file_name, 'w+') as f:
                f.write("{\n")
                for k, v in items.items():
                    if not v:
                        continue
                    f.write(f"    '{k}':\n        {v}, \n")
                f.write("}\n")

        output(f'OK')
    except Exception as e:
        output(f"Error: {e}")


class Res:
    O19_RESOURES_HELP = 'o19.res'
    O19_RESOURES_DUMP = O19_RESOURES_HELP + ".dump"
    O19_RESOURES_DATA = O19_RESOURES_HELP + ".data"
    O19_RESOURES_TYPES = O19_RESOURES_HELP + ".types"
    O19_RESOURES_HEXDUMP = O19_RESOURES_HELP + ".hexdump"
    O19_RESOURES_PRETTY = O19_RESOURES_HELP + ".pretty"
    O19_RESOURES_EMPTY = O19_RESOURES_HELP + ".empty"

    O19_RESOURES_HELP_TEXT = {
        O19_RESOURES_HELP: ': Show this help message',
        # output('o19.res.dump )')
        O19_RESOURES_DUMP: '[resource type]: Write all matching resource types, for "CLIP_HEADER", "CASPART" with the in-game name.',
        O19_RESOURES_DATA: ': Toggle dumping base game data (default) or CC data',
        O19_RESOURES_TYPES: ' [filter]: Write all valid [resource type] options to the console, optionally filter for a string (eg "clip").',
        O19_RESOURES_HEXDUMP: ' [n]: Create a hex dump of the 1st item with "n" bytes || if "n" is missing: toggle hexdump (disabled by default)',
        O19_RESOURES_PRETTY: ': Toggle pretty output format (default).',
        O19_RESOURES_EMPTY: ' : Toggle complete output format (default) or remove all packages without items.',
    }


@sims4.commands.Command(Res.O19_RESOURES_HELP, command_type=sims4.commands.CommandType.Live)
def o19_hh_sliders_help(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        for key, value in Res.O19_RESOURES_HELP_TEXT.items():
            output(key + value)
    except Exception as ex:
        output(f"{Res.O19_RESOURES_HELP}() Error: " + str(ex))


@sims4.commands.Command(Res.O19_RESOURES_DATA, command_type=sims4.commands.CommandType.Live)
def debug_o19_res_dump_data(_connection=None):
    global parse_mods
    output = sims4.commands.CheatOutput(_connection)
    parse_mods = not parse_mods
    output(f"Parse 'Mods' data is {parse_mods}. Parse 'Game' data is {not parse_mods}")


@sims4.commands.Command(Res.O19_RESOURES_PRETTY, command_type=sims4.commands.CommandType.Live)
def debug_o19_res_toggle_pretty(_connection=None):
    global dump_empty_packages
    output = sims4.commands.CheatOutput(_connection)
    dump_empty_packages = not dump_empty_packages
    output(f"Print empty packages is {dump_empty_packages}")


@sims4.commands.Command(Res.O19_RESOURES_EMPTY, command_type=sims4.commands.CommandType.Live)
def debug_o19_res_toggle_empty(_connection=None):
    global print_pretty
    output = sims4.commands.CheatOutput(_connection)
    print_pretty = not print_pretty
    output(f"Pretty output format is {print_pretty}")


@sims4.commands.Command(Res.O19_RESOURES_HEXDUMP, command_type=sims4.commands.CommandType.Live)
def debug_o19_res_toggle_hexdump(p_do_hex_dump = None, _connection=None):
    global do_hex_dump
    output = sims4.commands.CheatOutput(_connection)
    if p_do_hex_dump is None:
        if do_hex_dump == 0:
            do_hex_dump = 512
        else:
            do_hex_dump = 0
    else:
        do_hex_dump = int(p_do_hex_dump)
    output(f"Number of hex dump characters: {do_hex_dump} (0==disabled).")


@sims4.commands.Command(Res.O19_RESOURES_TYPES, command_type=sims4.commands.CommandType.Live)
def debug_o19_res_types(p_filter = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    keys = set(item.name for item in sims4.resources.Types)
    o = f"{len(keys)} resource types:"
    ln = len(o)
    max_len = 1024  # Console output seems to be limited to 1024 characters / line
    for k in keys:
        if p_filter and p_filter.upper() not in k:
            continue
        ln = ln + len(k) + 2
        if ln > max_len:
            output(f"{o}")
            o = f"{k}, "
            ln = len(o)
        else:
            o = f"{o} {k},"
    output(f"{o}")
    return

###############
def my_dump_test_2(x: bool=False):
    import os
    import re
    import ast
    mods_folder = os.path.expanduser(os.path.join('~', 'Documents', 'Electronic Arts', 'The Sims 4', 'Mods'))
    file_name = os.path.join(mods_folder, "items.mods.caspart.txt")

    # Play with regex_p - packages can be usually grouped together by removing everything behind the last or 2nd last underscore.
    # Removing '_nr' one works usually fine but some authors use '_nr_nr' after the item the name.
    regex_p = re.compile('_[^_]*$')
    if x:
        regex_p = re.compile('_[^_]*_[^_]*$')

    with open(file_name, 'rt') as fp:
        configuration_text = ""
        for line in fp:
            configuration_text = configuration_text + line
        fp.close()
        configuration = ast.literal_eval(configuration_text)

    short_name_2_ids = {}
    short_name_2_filename = {}
    mods_folder_len = len(mods_folder) + 1
    for filename, id_2_names in configuration.items():
        _filename = str(filename)[mods_folder_len:]
        for id, name in id_2_names.items():
            short_name = regex_p.sub('', name)
            _ids = short_name_2_ids.get(short_name, set())
            _ids.add(id)
            short_name_2_ids.update({short_name: _ids})

            _file_name = short_name_2_filename.get(short_name, set())
            _file_name.add(_filename)
            short_name_2_filename.update({short_name: _file_name})


    imp = {}
    for short_name, ids in short_name_2_ids.items():
        imp.update({short_name: ids})
    print("{")
    for short_name, v in imp.items():
        filenames = short_name_2_filename.get(short_name)
        print(f"'{short_name}': [{v}], # {filenames}")
    print("}")
my_dump_test_2()


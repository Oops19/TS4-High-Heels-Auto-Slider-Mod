#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#

class Oops19Constants:
    SIM_NAME_SEP = '#'  # 'Mary Kate_1' 'Ellis-Bextor-' <==> 'Mary Kate_1#Ellis-Bextor' (two-way as '#' is not allowed in names).

    # 'Marys: <Kate>#Elli's-Bextor' ==> Marys___Kate_#Elli_s-Bextor' (one-way conversion, _ is one of the special characters).
    SIM_FILENAME_SPACE = '_'
    # The Sims 4 allows random sim names. But we can not create a file with a few of them. They and a few more will be replaced with SIM_FILENAME_SPACE.
    # non-ASCII UCS-2 will stay as-is though. Eg 0x2019 == ’ will not be replaced.
    INVALID_FILENAME_CHARACTERS = '[\<\>\:\|\?\* \"\'\´\`\/\\\\]'


    # Final / Read-Only configurations
    DIRECTORY_INI = "ini"

    # Mod and custom user configurations (rw)
    DIRECTORY_CONFIGURATION = "configuration"

    # Write-Only output directory for everything except log files.
    # Data will likely not be read from here
    DIRECTORY_DUMP = "documents"

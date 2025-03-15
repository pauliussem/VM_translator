# VM translator to assembly language for "hack computer" implemented in course "From Nand To Tetris".
# NOTE. Translator doesn't include pointers for THIS and THAT.

import os

MEMORY_LOCATION_NAMES_TUPLE = ("local", "argument", "this", "that")
MEMORY_LOCATION_NAMES_DICT = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": "TEMP"}
ARITH_COMMANDS_TUPLE = ("add", "sub", "neg", "eq", "get", "gt", "lt", "and", "or", "not")

function_names = []
used_labels = []
my_list_of_lines = []
call_counter = 0
static_counter = 0

#TODO: Read necessary lines from a file and divide each line into a different list with split values.

def creating_a_list_with_necessary_lines(file_name):
    global function_names
    # Reading lines from a file, removing empty spaces and lines which begins with "//".
    with open(file_name, "r") as file:
        lines_list = file.read().splitlines()
        temp_list = [line.strip() for line in lines_list]
        relevant_lines = [line for line in temp_list if not line.startswith("//") and line != '']

        # Creating a list of lists of lines with separated values and checking for all functions.
        list_of_lines_lists = [line.split(" ") for line in relevant_lines]

        # Checking for all functions in a file.
        for function in list_of_lines_lists:
            if function[0] == "function":
                function_names.append(function[1])

    return list_of_lines_lists


#TODO: Check if there are no duplicates of labels and raise ValueError if there are.

def check_for_labels(my_list):
    global used_labels
    global my_list_of_lines
    for line in my_list:
        if line[0] == 'label':
            if used_labels and line[1] in used_labels:
                raise ValueError(f'label name "{line[1]}" appeared more than 1 time.')
            used_labels.append(line[1])


#TODO: Check operation and assign function depending on which operation it is.

def check_commands(my_list):
    global my_list_of_lines

    for line_index, line in enumerate(my_list):
        current_line = line

        # Checking the first word of a line and assigning relevant function.
        if line[0] == "function":
            handling_functions(current_line)
        elif line[0] in ARITH_COMMANDS_TUPLE:
            handling_arith_commands(current_line, line_index, my_list)
        elif line[0] in ("goto", "if-goto"):
            handling_goto(current_line)
        elif line[0] in ("push", "pop"):
            handling_memory_access(current_line)
        elif line[0] == "call":
            handling_call(current_line)
        elif line[0] == "label":
            handling_labels(current_line)
        elif line[0] == "return":
            handling_return(current_line)
        else:
            raise KeyError(f'In line "{line}" such key does not exist: "{line[0]}"')


# TODO: Collect all labels and check if label name fulfills label's name requirements.

def handling_labels(line):
    global my_list_of_lines
    my_string = ' '.join(map(str, line))

    # Checking if label name is not a number.
    try:
        int(line[1])
    except ValueError:
        pass
    else:
        raise ValueError(f'Label name must be a string.')

    # Checking if label name is not longer than 1 word.
    if len(line) > 2:
        raise SyntaxError(f'SyntaxError in line "{my_string}". Label name should be made from 1 word. '
                          f'You can use "_" to separate words.')
    else:
        my_list_of_lines.append(f'// {my_string}\n({line[1]})\n')


# TODO: Check where operation goto heads and append my_list_of_lines with relevant assembly instructions.

def handling_goto(line):
    global my_list_of_lines
    my_string = ' '.join(map(str, line))

    if len(line) > 2:
        raise SyntaxError(f'SyntaxError in line "{my_string}". Goto location must be 1 string.'
                          f'You can use "_" to separate words.')

    elif line[0] == "goto":
        my_list_of_lines.append(f'// {my_string}\n@{line[1]}\n0;JMP\n')


# TODO: Check syntax of a function and raise error if something is wrong.
#  Else append my_list_of_lines with relevant assembly instructions.

def handling_functions(line):
    global my_list_of_lines
    my_string = ' '.join(map(str, line))

    # Checking syntax of a function.
    try:
        int(line[1])
    except ValueError:
        pass
    else:
        raise ValueError(f'In line {my_string} function name must be a string.')

    try:
        int(line[2])
    except ValueError:
        raise ValueError(f'In line {my_string} nVars must be an integer.')

    if len(line) > 3:
        raise SyntaxError(f'In line "{my_string}".')

    # Append my_list_of_lines with function name and making space for LCL variables if necessary.
    my_list_of_lines.append(f'//{my_string}\n({line[1]})\n')

    if int(line[2]) > 0:
        lcl_places = int(line[2])
        while lcl_places > 0:
            my_list_of_lines.append(f'@SP\nA=M\nM=0\n@SP\nM=M+1\n')
            lcl_places -= 1


# TODO: Check syntax of operation call and if called function exists.

def handling_call(line):
    global my_list_of_lines
    global call_counter
    global function_names
    my_string = ' '.join(map(str, line))

    # Checking syntax of operation call.
    try:
        int(line[2])
    except ValueError:
        raise ValueError(f'In line {my_string} nArgs must be an integer.')

    if len(line) > 3:
        raise SyntaxError(f'In line "{my_string}".')

    # Checking if called function exists. If it does append my_list_of_lines with relevant assembly instructions.

    if line[1] not in function_names:
        raise KeyError(f'There is no such function called "{line[1]}"')
    else:
        my_list_of_lines.append(f'//{my_string}\n@RETURN_{line[1]}_{call_counter}\n'
                       f'//Return address save\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                       f'//LCL save\n@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                       f'//ARG save\n@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                       f'//THIS save\n@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                       f'//THAT save\n@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
                       f'//ARG reposition\n@{line[2]}\nD=A\n@5\nD=D+A\n@SP\nD=M-D\n@ARG\nM=D\n'
                       f'//LCL reposition\n@SP\nD=M\n@LCL\nM=D\n@{line[1]}\n0;JMP\n(RETURN_{line[1]}_{call_counter})\n')
        call_counter += 1


# TODO: Check syntax of return. If it's ok append my_list_of_lines with relevant assembly instructions.

def handling_return(line):
    global my_list_of_lines
    my_string = ' '.join(map(str, line))

    if len(line) > 1:
        raise SyntaxError(f'In line "{my_string}".')
    else:
        my_list_of_lines.append(f'//{my_string}\n'
                       f'//endFrame\n@LCL\nD=M\n@13\nM=D\n'
                       f'//return address\n@5\nD=A\n@13\nA=M-D\nD=M\n@14\nM=D\n'
                       f'//return value to argument 0\n@LCL\nA=M\nD=M\n@ARG\nA=M\nM=D\n'
                       f'//restoring SP\nD=A+1\n@SP\nM=D\n'
                       f'//restoring THAT\n@1\nD=A\n@13\nA=M-D\nD=M\n@THAT\nM=D\n'
                       f'//restoring THIS\n@2\nD=A\n@13\nA=M-D\nD=M\n@THIS\nM=D\n'
                       f'//restoring ARG\n@3\nD=A\n@13\nA=M-D\nD=M\n@ARG\nM=D\n'
                       f'//restoring LCL\n@4\nD=A\n@13\nA=M-D\nD=M\n@LCL\nM=D\n'
                       f'//goto return address\n@14\nA=M\n0;JMP\n')

#TODO: Check which memory access command is initialized and depending on memory location name
# append my_list_of_lines with relevant assembly code.


def handling_memory_access(line):
    global my_list_of_lines
    global static_counter
    my_string = ' '.join(map(str,line))

    # Checking if 3rd value of memory access command is an integer, else raising ValueError.
    try:
        my_int = int(line[2])
    except ValueError:
        raise ValueError(f'In line "{my_string}" value {line[2]} must be an integer.')

    # Checking if memory location name exists and if it does append my_list_of_lines with relevant assembly code,
    # else raising KeyError.

    # "Push" part:
    if line[0] == "push":
        if line[1] not in ("constant", "temp", "static", *(MEMORY_LOCATION_NAMES_TUPLE)):
            raise KeyError(f'In line "{my_string}" key "{line[1]}" is not recognized.')
        elif line[1] == "constant":
            my_list_of_lines.append(f"// {my_string}\n@{line[2]}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif line[1] in MEMORY_LOCATION_NAMES_TUPLE:
            my_list_of_lines.append(f"// {my_string}\n@{MEMORY_LOCATION_NAMES_DICT[line[1]]}\nD=M\n@{line[2]}\nA=D+A\n"
                                    f"D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif line[1] == "static":
            my_list_of_lines.append(f'// {my_string}\n@static.{line[2]}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        else:
            my_list_of_lines.append(f"// {my_string}\n@{my_int + 5}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

    # "Pop" part:
    else:
        if line[1] not in ("constant", "temp", "static", *(MEMORY_LOCATION_NAMES_TUPLE)):
            raise KeyError(f'In line "{my_string}" key "{line[1]}" is not recognized.')
        elif line[1] == "constant":
            my_list_of_lines.append(f"// {my_string}\n@{my_int}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif line[1] in MEMORY_LOCATION_NAMES_TUPLE:
            my_list_of_lines.append(f"// {my_string}\n@{MEMORY_LOCATION_NAMES_DICT[line[1]]}\nD=M\n@{my_int}\nA=D+A\n"
                                    f"D=A\n@13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@13\nA=M\nM=D\n")
        elif line[1] == "static":
            my_list_of_lines.append(f'// {my_string}\n@SP\nAM=M-1\nD=M\n@static.{static_counter}\nM=D\n')
            static_counter += 1
        else:
            if my_int+5 < 13 and my_int >= 0:
                my_list_of_lines.append(f"// {my_string}\n@{my_int + 5}\n@SP\nM=M-1\nA=M\nD=M\n@{my_int + 5}\nM=D\n")
            else:
                raise ValueError(f'Memory segment "temp" is out of range.')


# TODO: Check if arithmetic command exists in "hack computer's" CPU. If it does append my_list_of_lines with relevant
#  assembly code.
#  NOTE. This part includes handling if-goto operation.

def handling_arith_commands(line, line_index, my_list):
    global my_list_of_lines
    my_string = ' '.join(map(str, line))

    if line[0] == 'add':
        my_list_of_lines.append(f'// {my_string}\n@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D+M\n')
    elif line[0] == 'sub':
        my_list_of_lines.append(f'// {my_string}\n@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=M-D\n')
    elif line[0] == 'neg':
        my_list_of_lines.append(f'// {my_string}\n@SP\nM=M-1\nA=M\nD=M\nM=-M\n@SP\nM=M+1\n')

    # Assigning conditional goto label from next line after arithmetic operation.
    elif line[0] == 'eq':
        my_list_of_lines.append(f'// {my_string}\n@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n@{my_list[line_index + 1][1]}\nD;JEQ\n')
    elif line[0] == 'gt':
        my_list_of_lines.append(f'// {my_string}\n@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n@{my_list[line_index + 1][1]}\nD;JGT\n')
    elif line[0] == 'lt':
        my_list_of_lines.append(f'// {my_string}\n@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n@{my_list[line_index + 1][1]}\nD;JLT\n')

    elif line[0] == 'and':
        my_list_of_lines.append(f'// {my_string}\n@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nM=M&D\n@SP\nM=M+1\n')
    elif line[0] == 'or':
        my_list_of_lines.append(f'// {my_string}\n@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nM=M|D\n@SP\nM=M+1\n')
    elif line[0] == 'not':
        my_list_of_lines.append(f'// {my_string}\n@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=!M\n@SP\nM=M+1\n')
    else:
        raise ValueError(f'No such arithmetic command "{line[0]}" in "hack computer".')


# TODO: Ask to enter file path, check file name and create file with same name, but .asm extension.

def main():
    global my_list_of_lines

    # Append my_list_of_lines with assigned memory locations for memory segments.
    my_list_of_lines.append(f'@256\nD=A\n@SP\nM=D\n@500\nD=A\n@LCL\nM=D\n@600\nD=A\n@ARG\nM=D\n'
                            f'@700\nD=A\n@THIS\nM=D\n@800\nD=A\n@THAT\nM=D\n')

    # Handling file after file path is entered. Assembly code is appended to my_list_of_lines.
    file_path = os.path.join(input("Please enter file path (without quotes): "))
    check_commands(creating_a_list_with_necessary_lines(file_path))

    # Creating new file with the same name, but .asm extension.
    file_name = os.path.basename(file_path).split('/')[-1]
    asm_file = file_name.replace(".txt", ".asm")

    with open(asm_file, "a") as file:
        temp_list = [''.join(my_list_of_lines)]
        file.write(' '.join(temp_list))

main()
#CIT 591 Homework #4: HTML Tidy
#Authors: Alifia Haidry and Anders Schneider

import os
import Tkinter
import tkFileDialog
import random
import sys

empty_content_tags = ['area', 'base', 'basefont', 'br', 'col', 'frame', 'hr',
                      'img', 'input', 'isindex', 'link', 'meta', 'param']
#The list below is set so as to make testing possible. It is reset to an empty
#list at the beginning of running the main function
global_start_tag_list = ["xyz", "abc", "def"]
max_line_length = 80

def process_start_tag(line, position):
    """ Searches for a start tag in a line and returns it. """
    
    tag = ''
    position = position + 1
    while line[position] != ">" and line[position] != ' ':
        tag = tag + line[position]
        position = position + 1
    return tag.lower()


def process_end_tag(line, position):
    """ Searches for a end tag in a line and returns it. """
    
    end_tag = ''
    position = position + 2
    while line[position] != '>':
        end_tag = end_tag + line[position]
        position = position + 1
    return end_tag.lower()


def insert_end_tag(line, position, start_tag_list):
    """Inserts the an end tag corresponding to the final start tag in a
    list and returns the line, position, and start tag list"""

    global global_start_tag_list
    tag_to_insert = start_tag_list.pop()
    global_start_tag_list.pop()
    
    line = (line[:position] + '</' + tag_to_insert.lower() + '>' +
            line[position:])

    position = position + len(tag_to_insert) + 3

    return line, position, start_tag_list


def correct_capitalization(line, position, tag, is_start_tag):
    """Converts all tags into lowercase and returns the modified line."""
    
    if is_start_tag:       
        line = line[:position] + "<" + tag.lower() + line[position + 1
                                                          + len(tag):]
    else:
        line = line[:position] + "</" + tag.lower() + line[position
                                                           + 2 + len(tag):]

    return line


def start_tag_function(line, position, start_tag_list):
    """Inserts start tags to the local and global start tag lists and
    returns line, position and start tag list. """

    global global_start_tag_list
    tag = process_start_tag(line, position)

    line = correct_capitalization(line, position, tag, True)
    position = position + 1 + len(tag)

    if tag == 'pre':

        if line.find("</pre>", position) != -1:
            #Between pre tags, simply advance the position
            while line[position : position + 6] != "</pre>":
                position = position + 1
            position = position + 5

        else:
            start_tag_list.append(tag)
            global_start_tag_list.append(tag)
            position = len(line)
    
    elif tag not in empty_content_tags:
        start_tag_list.append(tag)
        global_start_tag_list.append(tag)

    return line, position, start_tag_list


def end_tag_function(line, position, start_tag_list, end_tag_list):
    """If end tag matches the last element of the start tag list, then the
    last element is popped. If it does not match then the end tag is
    compared with the global list. If present in the global list, it is
    added to the end tag list. If it is not present in the global list
    then the end tag is removed from the line. If end tag is missing,
    inserts an end tag. """
    
    global global_start_tag_list
    end_tag = process_end_tag(line, position)
    line = correct_capitalization(line, position, end_tag, False)
    counter = 0
    while counter < 2:

        #The case where the end tag matches the last start tag
        if start_tag_list != [] and end_tag == start_tag_list[-1]:
            start_tag_list.pop()
            global_start_tag_list.pop()
            position = position + 3 + len(end_tag)
            break

        #The case where the end tag does not match any previous end tag
        elif start_tag_list == [] and end_tag not in global_start_tag_list:
            counter = 2
            break

        #The case where the end tag matches a start tag from a previous line
        elif start_tag_list == [] and end_tag in global_start_tag_list:
            position = position + 3 + len(end_tag)
            end_tag_list.append(end_tag)
            break

        #The case where the end tag does not match and we insert one
        else:
            (line, position, start_tag_list) = insert_end_tag(line, position,
                                                              start_tag_list)
            counter = counter + 1

    #If the end tag does not match after two insertions, remove it
    if counter == 2: 
        end_tag_length = len(end_tag) + 3
        line = line[:position] + line[position + end_tag_length:]
        
    return line, position, start_tag_list, end_tag_list


def correct_tag_nesting(line):
    """ Corrects the nesting of start tags and end tags in a line """

    end_tag_list = []
    global global_start_tag_list
    start_tag_list = []
    position = 0

    while position < len(line):
        
        #Checking to see if we've found a start tag
        if line[position] == "<" and (65 <= ord(line[position + 1]) <= 91
                                      or 97 <= ord(line[position + 1]) <= 122):
            (line, position, start_tag_list) = start_tag_function(line,
                                                                  position,
                                                                  start_tag_list)

        #Checking to see if we've found an end tag
        elif (position < (len(line) - 1)
              and line[position : position + 2] == "</"):
            
            (line, position, start_tag_list, end_tag_list) = end_tag_function(
                                                                line,
                                                                position,
                                                                start_tag_list,
                                                                end_tag_list)

        else:
            position = position + 1

    return line, start_tag_list, end_tag_list


def dealing_with_special_tags(line):
    """ Places a line break above special tags. """
    
    special_tags = ['head', 'body', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

    for tag in special_tags:

        pos = line.find("<" + tag + ">")
        while pos != -1:
            line = line[: pos] + "\n" + line[pos:]
            pos = line.find("<" + tag + ">", pos + len(tag) + 3)

    return line


def start_tag_correct_indentation(line, indentation, start_tag_list):
    """Corrects the indentation of start tags. """
    
    start_point = 0
    additional_indentation = 0

    for tag in start_tag_list:
        end_point = line.find("<" + tag, start_point)

        #The case where the start tag does not begin the line:
        if end_point != indentation * 2:
            line = (line[:end_point] + "\n"
                    + (indentation + additional_indentation) * '  '
                    + line[end_point:])
        start_point = end_point + 1
        additional_indentation = additional_indentation + 1

    return line, indentation, start_tag_list


def end_tag_correct_indentation(line, indentation, end_tag_list):
    """Corrects the indentation of end tags. """
    
    global global_start_tag_list
    start_point = 0
    subtract_indentation = 1
    i = 0

    for tag in end_tag_list:
        end_point = line.find("</" + tag, start_point)

        #The case where the end tag is </pre>:
        if tag == "pre":
            global_start_tag_list.pop()
            subtract_indentation = subtract_indentation + 1
            break

        #The case where the end tag begins the line
        elif end_point == indentation * 2:
            line = line[2:]

        else:

            #The case where the end tag is at the end of the line:
            if len(line) == end_point + 3 + len(tag):
                line = (line[:end_point] + "\n"
                        + (indentation - subtract_indentation) * '  '
                        + line[end_point:])

            #The case where the end tag is in the middle of the line:
            else:
                if i < len(end_tag_list) - 1:
                    next_item = end_tag_list[i+1]
                else:
                    next_item = "dummy"

                #The case where the next tag directly follows this end tag
                #(only add a new line before the end tag):
                if (line.find("</" + next_item, end_point) == (end_point + 3
                                                               + len(tag))
                    or (end_point + 3 + len(tag) == len(line) - 1)):
                    
                   line = (line[:end_point] + "\n"
                           + (indentation - subtract_indentation) * '  '
                           + line[end_point:end_point + 3 + len(tag)]
                           + line[end_point + 3 + len(tag):])

                #The case where the end tag is followed by text
                #(add a new line before and after the end tag):
                else:
                    line = (line[:end_point] + "\n"
                            + (indentation - subtract_indentation) * '  '
                            + line[end_point:end_point + 3 + len(tag)]
                            + "\n"
                            + (indentation - subtract_indentation) * '  '
                            + line[end_point + 3 + len(tag):])

            start_point = end_point + 1

        global_start_tag_list.pop()
        subtract_indentation = subtract_indentation + 1
        i = i + 1

    return line, indentation, end_tag_list


def correct_indentation(line, indentation, start_tag_list, end_tag_list):
    """Corrects the indentation of the complete line. """
    
    global global_start_tag_list

    #Handling lines in between pre tags
    if (global_start_tag_list != [] and global_start_tag_list[-1] == "pre"
        and "</pre>" not in line and start_tag_list == []):
        
        pass

    #Handling the last line of pre tag situation
    elif (global_start_tag_list != [] and global_start_tag_list[-1] == "pre"
          and "</pre>" in line):
        
        global_start_tag_list.pop()

    #Handling a case where the line contains unmatched start or end tags
    elif start_tag_list != [] or end_tag_list != []:
        line = indentation * '  ' + line

        #Line contains unmatched end tags:
        if end_tag_list != []:
            (line, indentation, end_tag_list) = end_tag_correct_indentation(
                                                                line,
                                                                indentation,
                                                                end_tag_list)

        #Line containes unmatched start tags
        if start_tag_list != []:
            (line, indentation, start_tag_list) = start_tag_correct_indentation(
                                                                line,
                                                                indentation,
                                                                start_tag_list)

    #Line only consists of text and matched start/end tags
    else:
        line = indentation * '  ' + line

    return line


def generate_line_list(break_pos, line_list, pos, line):
    """Generates a list of sublines to be used for line length
    correction, and returns the list. """

    while break_pos != -1:
        line_list.append(line[pos:break_pos])
        pos = break_pos
        next_break_pos = line.find("\n", pos + 1)
        if next_break_pos == -1:
            line_list[-1] = line_list[-1] + "\n"
        break_pos = next_break_pos

    return line_list


def separate_line_into_segments(sub_line, line_list, i):
    """If a line is above the maximum length, this function
    breaks it into appropriately sized pieces, which are stored
    in the line_list."""

    new_line_char = 0
    char = 0
    while sub_line[char] == '\n':
        new_line_char = new_line_char + 1
        char = char + 1
    while sub_line[char] == ' ':
        char = char + 1
    local_indentation = char - new_line_char
    char = max_line_length
    while sub_line[char] != ' ':
        char = char - 1
        if char == 0:
            break
    
    sub_line1 = sub_line[:char + 1]
    sub_line2 = "\n" + local_indentation * ' ' + sub_line[char + 1:]

    line_list[i] = sub_line1
    line_list.insert(i + 1, sub_line2)

    return sub_line1, line_list


def line_length_correction(line):
    """Breaks up lines longer than 80 characters, and removes whitespace
    at the end of each line"""
    
    if line[-1] != "\n":
        line = line + "\n"
        
    line_list = []
    pos = 0
    break_pos = line.find("\n", pos)

    if break_pos == -1:
        line_list.append(line)
    else:
        line_list = generate_line_list(break_pos, line_list, pos, line)

    i = 0
    for sub_line in line_list:

        #Break the line into smaller segments (if necessary)
        if len(sub_line) > max_line_length:
            (sub_line1, line_list) = separate_line_into_segments(sub_line,
                                                                 line_list, i)
        else:
            sub_line1 = sub_line

        #Remove the whitespace at the end of each line
        if (global_start_tag_list != []
            and global_start_tag_list[-1] != 'pre'
            or global_start_tag_list == []):
            (sub_line1, line_list) = remove_end_whitespace(sub_line1,
                                                           line_list, i)
        i = i + 1
    new_line = ''
    
    for sub_line in line_list:
        new_line = new_line + sub_line

    return new_line


def remove_end_whitespace(sub_line1, line_list, i):
    """Removes white spaces from the end of a line. """
    
    while len(sub_line1) > 1 and sub_line1[-2] == ' ':
        sub_line1 = sub_line1[:len(sub_line1) - 2] + "\n"
        line_list[i] = sub_line1

    return sub_line1, line_list


def process_input_file(line, output_file):
    """Processes the input file and writes it to the output file. """
    
    global global_start_tag_list
    indentation = len(global_start_tag_list)

    #First we correct the nesting of the tags within the line
    if global_start_tag_list == []:
        (line, start_tag_list, end_tag_list) = correct_tag_nesting(line)
    elif global_start_tag_list != [] and global_start_tag_list[-1] != "pre":
        (line, start_tag_list, end_tag_list) = correct_tag_nesting(line)
    elif global_start_tag_list != [] and global_start_tag_list[-1] == "pre":
        start_tag_list = []
        end_tag_list = []

    #Second we take into account tags like <head> or <h1>    
    line = dealing_with_special_tags(line)

    #Third we give the line the correct indentation
    line = correct_indentation(line, indentation, start_tag_list,
                               end_tag_list)

    #Fourth we correct the length of the line and remove whitespace
    line = line_length_correction(line)

    #Finally we write the corrected line to the output file
    output_file.write(line)

   
def make_output(file_path):
    """ Reads the input file, generates the output file and returns the
    output file name. """

    infile = open(file_path, "r")
    output_file_name = str(random.randint(1, sys.maxint))
    output_file = open(output_file_name + '.html', 'w')
    while True:
        line = infile.readline()
        if len(line) == 0:
            break
        process_input_file(line, output_file)
    output_file.close()
    infile.close()
    return output_file_name + '.html'


def replace_input(infile_name, outfile_name):
    """ Removes the input file and renames the output file as input file
    name. """ 
    os.remove(infile_name)
    os.rename(outfile_name, infile_name)


def open_html_file():
    """Opens the Input file and returns its path. """
 
    Tkinter.Tk().withdraw() 
    in_path = tkFileDialog.askopenfilename()
    open_file = open(in_path, 'r')
    open_file.close()
    return in_path


def make_backup(file_path):
    """ Makes backup of the input file with .html.bak extension. """

    infile = open(file_path, "r")
    name = os.path.basename(file_path)
    backup_file = open(name + '.bak', 'w')
    while True:
        text = infile.readline()
        if len(text) == 0:
            break
        backup_file.write(text)
    infile.close()
    backup_file.close()

    return name


def main():

    global global_start_tag_list
    global_start_tag_list = []

    input_file_path = open_html_file()
    infile_name = make_backup(input_file_path)
    outfile_name = make_output(input_file_path)
    replace_input(infile_name, outfile_name)

if __name__ == "__main__":
    main()

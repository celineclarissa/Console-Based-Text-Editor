'''
Console-Based Text Editor

Name: Celine Clarissa Chandra

Background

I am a freshman data science student building foundational programming skills
through hands-on projects. This editor was developed as an assignment of a course
in university to reinforce key concepts in string handling, user input
parsing, and command execution flow—all within a non-object-oriented,
procedural programming approach.


Problem Statement

Build and design a simple but powerful single-line editor requires
handling many aspects of user interaction, including cursor movement,
character-wise editing, command parsing, and maintaining edit history.
The goal of this assignment is to simulate a real text editing environment
in the command line, complete with helpful features like undo and command
repetition, using only fundamental Python programming techniques.
'''

# Import library
import re

# Initialize variables
text = ''
cursor_on = False
cursor_pos = 0
history = [('', '', 0)]
help_message = '''? - display this help info
. - toggle row cursor on and off
h - move cursor left
l - move cursor right
^ - move cursor to beginning of the line
$ - move cursor to end of the line
w - move cursor to beginning of next word
b - move cursor to beginning of previous word
i - insert <text> before cursor
a - append <text> after cursor
x - delete character at cursor
dw - delete word and trailing spaces at cursor
u - undo previous command
r - repeat last command
s - show content
q - quit program'''

# Helper functions
def run(user_input:str):
    '''
    Executes another function (command) according to the user's input.
    If the user's input is out of the scope of the options, this function will do nothing.
    Exits the program if the user inputs a certain character.

    Parameter:
    user_input (str)    : The input of the user.
                          (Can contain only 1-2 characters or
                          some words depending on the command).
    '''
    options = {'?': lambda: print(help_message),
               '.': toggle_cursor,
               'h': lambda: move_cursor(-1),
               'l': lambda: move_cursor(1),
               '^': lambda: move_cursor(-cursor_pos-1),
               '$': lambda: move_cursor(len(text)-cursor_pos),
               'w': move_next_word,
               'b': move_prev_word,
               'i': lambda: manipulate_text(cursor_pos, cursor_pos, 0, user_input[1:]),
               'a': lambda: manipulate_text(cursor_pos+1, cursor_pos+1, len(text+user_input[1:])-1, user_input[1:]),
               'x': lambda: manipulate_text(cursor_pos, cursor_pos+1, -1 if cursor_pos > len(text) else 0),
               'dw': delete_word,
               'u': undo_previous,
               'r': repeat_last_command,
               's': lambda: print(text)}
    if user_input == 'q':
        exit()
    elif user_input in ['', 'i', 'a']:
        main()
    elif user_input[0] in ['i', 'a'] or (user_input in options):
        options[user_input[0] if user_input[0] in ['i', 'a'] else user_input]()
        if text and user_input not in ['?', 'r', 's', 'u']:
            history.append((user_input, text, cursor_pos))      

# Cursor display functions
def turn_on_cursor(content:str) -> str:
    '''
    Returns an updated version of content with the cursor enabled for display.

    Parameter:
    content (str): The original content with its cursor turned off.
    '''
    global cursor_pos
    try:
        return content[:cursor_pos]+'\033[42m'+content[cursor_pos]+'\033[0m'+content[cursor_pos+1:]
    except IndexError:
        if cursor_pos > 0:
            return content[:cursor_pos-1]+'\033[42m'+content[cursor_pos-1]+'\033[0m'+content[cursor_pos:]
        return content

def turn_off_cursor(content:str) -> str:
    '''
    Returns an updated version of content with the cursor disabled for display.

    Parameter:
    content (str): The original content with its cursor turned on.
    '''
    translation = {'\033[42m':'', '\033[0m':''}
    regex = re.compile('|'.join(map(re.escape, translation)))
    return regex.sub(lambda match: translation[match.group(0)], content)

def toggle_cursor():
    '''
    Toggles the cursor display on or off by modifying the text.
    If the cursor is currently enabled, it is removed. Otherwise, it is added.
    '''
    global text, cursor_on, cursor_pos
    text = turn_off_cursor(text) if cursor_on else turn_on_cursor(text)
    cursor_on = not cursor_on
    if text:
        print(text)

# Cursor movement functions
def move_cursor(delta:int):
    '''
    Moves the cursor by the specified delta.
    Initiates user to enter another input if the text is empty.

    Parameter:
    delta (int) : The number of positions to move the cursor.
                  (A positive value moves the cursor forward/right,
                   a negative value moves the cursor backward/left).
    '''
    global text, cursor_pos, cursor_on
    if text == '':
        main()

    text = turn_off_cursor(text)
    cursor_pos = max(0, min(len(text), cursor_pos+delta))
    text = turn_on_cursor(text) if cursor_on else text
    print(text)

def move_prev_word():
    '''
    Moves the cursor to the beginning of the previous word (word to the left of the current word).
    If no word exists in that direction, the cursor remains stationary.
    '''
    global text, cursor_pos
    text = turn_off_cursor(text)
    indices = sorted([match.start() for match in re.finditer(r"\s", text)]+[0, len(text)])

    for i in range(1, len(indices)-1):
        if indices[i]-cursor_pos == -1 and indices[i-1]==0: # for words located at the beginning of the sentence
            move_cursor(-cursor_pos)
            break
        elif indices[i]-cursor_pos == -1:  # if the cursor at the exact start of a word, move it to the previous word
            move_cursor(indices[i-1]-cursor_pos+1)
            break
        elif indices[i] < cursor_pos <= indices[i+1]:   # if the cursor is within a word, move it to the start or move cursor to previous word
            move_cursor(indices[i]-cursor_pos+1)
            break
    
    if indices[0] < cursor_pos < indices[1]: # if cursor is at the first word, but not at the exact start
        move_cursor(0)

def move_next_word():
    '''
    Moves the cursor to the beginning of the next word (word to the right of the current word).
    If no word exists in that direction, the cursor remains stationary.
    '''
    global text, cursor_pos
    text = turn_off_cursor(text)
    indices = sorted([match.start() for match in re.finditer(r"\s", text)]+[0, len(text)])

    if indices[-2] < cursor_pos <= indices[-1]: # for words located at the end of the sentence
        move_cursor(0)
    else:
        for i in range(1, len(indices)-1):
            if indices[i] == cursor_pos:    # if cursor is positioned at space
                move_cursor(1)
                break
            elif indices[i] > cursor_pos:   # if cursor is positioned on a word
                move_cursor(indices[i]-cursor_pos+1)
                break

# Text manipulation functions
def manipulate_text(begin:int, end:int, delta:int, inserted_text=''):
    '''
    Modifies the text by replacing the content between "begin" and "end" with "inserted_text".
    Moves the cursor according to the delta.

    Parameters:
    begin (int)         : The position (index) where the text manipulation starts.
    end (int)           : The position (index) where the text manipulation ends.
    delta (int)         : The distance where the cursor needs to be moved after manipulating text.
    inserted_text (str) : The text that is going to be inserted between "begin" and "end".
                          (Default: '').
    '''
    global text
    text = turn_off_cursor(text)
    text = text[:begin] + inserted_text + text[end:]
    if cursor_pos == len(text):
        move_cursor(-1)
    else:
        move_cursor(delta)

def delete_word():
    '''
    Deletes a word at or after the cursor position.
    Moves the cursor to the start of the next word.
    '''
    global text, cursor_pos
    text = turn_off_cursor(text)

    indices = sorted([match.start() for match in re.finditer(r"\s", text)]+[0, len(text)])
    for i in range(len(indices)-1):
        if indices[i] <= cursor_pos <= indices[i+1]:
            begin, end = indices[i], indices[i+1]
            break
    if cursor_pos == 0:
        end = indices[1] if len(indices) > 1 else len(text)

    text = (text[:begin]+text[end:]).lstrip()

    for i in indices:
        if begin == 0:
            move_cursor(-cursor_pos)    # for words located at the beginning
            break
        elif end <= i:    # for words located in the middle of the sentence
            move_cursor(begin-cursor_pos+1)
            break

# Command history functions
def undo_previous():
    '''
    Undoes the previous command by restoring the last text state.
    If there is no command prior, users will be initiated to insert a new input.
    '''
    global text, history, cursor_pos
    if len(history) > 1:
        history.pop()
        text, cursor_pos = history[-1][1], history[-1][2]
        if text:
            print(text)
    else:
        main()

def repeat_last_command():
    '''
    Repeats the last executed command.
    '''
    last_command = history[-2][0] if (history and history[-1][0] in ['?', 'u', 'r']) else history[-1][0]

    if (last_command[0] in ['i', 'a']) or (last_command in ['.', 'h', 'l', '^', '$', 'w', 'b', 'x', 'dw', 's']):
        run(last_command)

# Run program
def main():
    '''
    Keeps the program running:
    Initiates user to input a string of characters,
    and run another function according to the input.
    '''
    while True:
        run(input('>'))

if __name__ == '__main__':
    main()
import csv
import os
from collections import defaultdict, deque #from data structures
import time

def main():
    #Prompt user for a Turing Machine file
    f = input("Please enter which Turing Machine would you like to evaluate: ")
    if os.path.exists(f):
        name, Q, alphabet, tape, start, accept, reject, transitions = parse_input_file(f) #Call parsing function to extract components
    else:
        print("No such file exists.")
    print(" ")
    
    #Display elements of the Turing Machine
    print(f"This Turing Machine is: {name}")
    print(f"The states are: {Q}")
    print(f"The alphabet is: {alphabet}")
    print(f"The tape characters are: {tape}")
    print(f"The start state is {start}, the reject state is {reject}, and the accept state is {accept}")
    print(f"The transitions are: {transitions}")
    print(" ") 
    
    #Promt user for an input string   
    input_string = input("Please enter the string you would like to input into the Turing Machine: ")
    checked = check_input_string(alphabet, input_string) #Call checking function to make sure the input string is in the alphabet
    while (checked == False): #If the input string is not in the alphabet, keep prompting the user for a string in the alphabet.
        next_try = input(f"Invalid String. Please input a string included in the alphabet - {alphabet}: ")
        checked = check_input_string(alphabet, next_try)
        if (checked == True):
            input_string = next_try #Once the user enters a valid string, set it as the new input string
            
    transition_dict = parse_transitions(transitions)
    start = time.time()
    tm(name, start, accept, reject, transition_dict, input_string)
    end = time.time()
    total_time = end - start
    print(f"Elapsed time: {total_time} seconds")
    
    another_string = True
    while another_string == True:
        another = input("Would you like to try another string (yes/no)? ")
        if another == 'no':
            another_string = False
            continue
        while another == 'yes':
            input_string = input("Please enter the string you would like to input into the Turing Machine: ")
            checked = check_input_string(alphabet, input_string) #Call checking function to make sure the input string is in the alphabet
            while (checked == False): #If the input string is not in the alphabet, keep prompting the user for a string in the alphabet.
                next_try = input(f"Invalid String. Please input a string included in the alphabet - {alphabet}: ")
                checked = check_input_string(alphabet, next_try)
                if (checked == True):
                    input_string = next_try #Once the user enters a valid string, set it as the new input string
            start = time.time()
            tm(name, start, accept, reject, transition_dict, input_string)
            end = time.time()
            total_time = end - start
            print(f"Elapsed time: {total_time} seconds")
            another = input("Would you like to try another string (yes/no)? ")
            if another == 'no':
                another_string = False
                break 
                
def parse_input_file(f):
    '''Parse the Turing Machine file and extract the elements'''
    elements = []
    with open(f, 'r') as file:
        csv_file = csv.reader(file)  # use the csv library
        for line in csv_file:
            elements.append(line) #put the lines of the tm descriptor file into a list (makes is simpler for me to visualize/parse)
    
    #Assign each element of the tm a value based on the project document
    name = elements[0][0]
    Q = list(elements[1])
    alphabet = list(elements[2])
    tape = list(elements[3])
    start = elements[4][0]
    accept = elements[5][0]
    reject = elements[6][0]
    transitions = elements[7:]

    return name, Q, alphabet, tape, start, accept, reject, transitions #return the elements to be called by later functions
    
def check_input_string(alphabet, input_string):
    '''Check to see if the input string is in the alphabet of the given Turing Machine'''
    for s in input_string:
        if s not in alphabet:
            return False
    return True

def parse_transitions(transitions):
    '''Convert transitions into a dictionary'''
    transition_dict = defaultdict(list)
    
    #generate the dictionary from the list of transitions with the key as the current state with the read character, and the value as the next state, tape char, and the direction
    for transition in transitions:
        state, read_char, next_state, tape_char, direction =  transition
        transition_dict[(state, read_char)].append((next_state, tape_char, direction))    
    return transition_dict
        
def tm(name, start, accept, reject, transition_dict, input_string):
    '''Turing Machine execution using bfs'''
    tape = list(input_string)
    head = 0 #begin at the beginning position of the input string
    state = start #begin at the start state
    depth = 0 #starting depth of the tree
    max_depth = 50 #so there will be no infinite loop (can be adjusted)
    print(f"Simulating Turing Machine: {name}")
    print(f"Input string: {input_string}")
    print(f"Initial configuration: {tape}")
    
    queue = deque([(state, tape, head, depth)])  # Queue holds configurations
    visited = set() #created a visited set (kind of like in a shortest pathfinding algorithm) to avoid visiting the same configuration
    steps = 0
    
    while queue: #execute while the queue is not empty
        steps += 1
        current_state, current_tape, current_head, current_depth = queue.popleft() #In each iteration, the first node in the queue is dequeued using popleft for bfs
        print_configuration(current_tape, current_head, current_state)
        if current_state == accept: #check to see if the accept state has been reached
           print(f"String accepted in {steps} steps and depth {depth - 1}.")
           return
        if current_state == reject: #stop traversing the current path
            continue
        if (tuple(current_tape), current_head, current_state) in visited: #check for repeat of configuration and skip it
            continue
        visited.add((tuple(current_tape), current_head, current_state)) #add the current configuration to the visited set
        next_configs = step(current_state, current_tape, current_head, transition_dict)
        if next_configs is None:
            continue #reject path   
        for next_state, next_tape, next_head in next_configs:
            queue.append((next_state, next_tape, next_head, current_depth + 1))
        depth += 1 #increment depth after traversing a level        
        if depth > max_depth:
            print(f"Execution stopped after {max_depth} steps.")
            return
        
    print(f"String rejected after {steps} steps.")
        
def step(state, tape, head, transition_dict):
    '''Execute one step of the Turing Machine''' 
    # Ensure that the tape can be accessed (expand if necessary)
    if head < 0:  # Head moved to the left beyond the first position
        tape = ['_'] + tape
        head = 0  # Correct head position to 0
    elif head >= len(tape):  # Head moved to the right beyond the last position
        tape.append('_')  # Add a blank to the right
    
    current_char = tape[head]
    
    if (state, current_char) not in transition_dict:
        return None  # No valid transition, reject path
    
    transitions = transition_dict[(state, current_char)]
    new_configurations = []
    
    for next_state, tape_char, direction in transitions:
        # Create a copy of the tape and modify it
        new_tape = tape[:]
        new_tape[head] = tape_char
        
        # Move the head, L = Left, R = Right
        if direction == 'L':
            new_head_pos = head - 1
        elif direction == 'R':
            new_head_pos = head + 1
        else:
            new_head_pos = head  # No movement if direction is '_'

        # Prevent accessing out-of-bounds head positions in future steps
        if new_head_pos < 0:
            new_head_pos = 0  # Do not let the head move out of bounds on the left
        elif new_head_pos >= len(new_tape):
            new_tape.append('_')  # Extend the tape to the right if needed

        new_configurations.append((next_state, new_tape, new_head_pos))

    return new_configurations

def print_configuration(tape, head, state):
    '''Print the current configuration of the Turing Machine'''
    left_of_head = ''.join(tape[:head])  # All characters left of head
    head_char = tape[head]  # Character under the head
    right_of_head = ''.join(tape[head + 1:])  # All characters right of head

    print(f"{left_of_head}{state}{head_char}{right_of_head}") #print out the current configuration (format described in assignment document)
          
if __name__ == "__main__":
    main()   
    
from libs.pySpacebrew.spacebrew import Spacebrew
from pythonosc import udp_client
import random
import time

######################### SPACEBREW CONFIGURATION ##########################################

# Information for spacebrew
app_name = "Backend"
description = "This app receives, processes and sends command back and forth between devices."
server = "192.168.0.7"
port = 6545
dead = False

# Create a spacebrew client instance
brew = Spacebrew(app_name, description=description, server=server)
client = udp_client.SimpleUDPClient(server,port)
# Add the basic pub/subs
brew.addPublisher("Send Command", "string")
brew.addSubscriber("Receive Command", "string")


##################### COMMAND HANDLER ##################################

# Receive commmands and process them
def commandHandler(command):
    '''
    This handler is in charge of receiving every command from every device.
    It will read the command, parse it and execute functions accordingly.
    It receives a command string and returns nothing.

    The string has a specific structure
    id:triggered_action:args

    where
    id               --> an int representing the identifier of the device.
    triggered_action --> a string identifying what action triggered the command.
    args             --> [Optional] a list of comma separated key=value pairs.

    Example:
    4:skip_button_pressed:time=19.78,x=16,y=19

    id = 4
    triggered_action = skip_button_pressed
    args = {'time': '19.78','x': '16','y': '19'}
    '''

    # Ensure command follows protocol
    assert ":" in command, "Malformed command. Not following protocol"
    command_list = command.split(":")
    command_list = list(filter(None, command_list))

    # Ensure theres at least 2 items inside the command
    assert len(command_list) > 1, "Malformed command. Missing values"
    assert len(command_list) < 4, "Malformed command. Too many values"

    # Get the id
    id = int(command_list[0])

    # Get the triggered_action
    trigger = command_list[1]

    # Get the args
    args = {} # Create an empty dictionary

    if len(command_list) == 3:
        # Add arguments to the dictionary
        raw_arguments = command_list[2]
        argument_list = raw_arguments.split(",") #=> ["time=19.78", "x=16", "y=19"]
        for argument in argument_list:
            assert "=" in argument, "Malformed argument. Not following protocol"
            key_value_arg = argument.split("=") #=> ["time", "19.78"]
            args[key_value_arg[0]] = key_value_arg[1]


    ################## ADD YOUR OWN COMMANDS HERE ########################
    if trigger == "skip_button_pressed":
        trigger_arp3()
    elif trigger == "id_requested":
        # TODO: assign and send the id to the device
        _ = 0 # toy command
    elif trigger == "seekbar_changed":
        change_a3feedback(int(args["progress"]))
    else:
        unknown_command(id, command)


brew.subscribe("Receive Command", commandHandler)
brew.start()

print("Server started!")
print("Spacebrew server listening at {0}".format(server))
print("OSC server using port {0}".format(port))


######################### FUNCTIONS #####################################

def trigger_arp3():
    val = 1
    client.send_message("/arp3",val)

def change_a3feedback(progress_val):
    '''
    This function receives an int between 0 and 255.
    It sends this value to pure data to change feedback percentage on arp3.
    It returns nothing
    '''
    max_input = 255.0
    max_output = 0.9
    feedback = progress_val/max_input*max_output
    print(feedback)
    client.send_message("/a3feedback",feedback)

def unknown_command(device_id, command):
    print("Received unknown command: " + command)
    brew.publish("Send Command", "{0}:unknown_command".format(device_id))

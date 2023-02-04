import board
from digitalio import DigitalInOut, Direction, Pull
import time

print("Hello World!")

# GPIO Ports:
print(dir(board))
door_is_open = DigitalInOut(board.GP15)
door_is_open.direction = Direction.INPUT
door_is_open.pull = Pull.DOWN

door_expected_open = DigitalInOut(board.GP28)
door_expected_open.direction = Direction.INPUT
door_expected_open.pull = Pull.DOWN

three_way_relay = DigitalInOut(board.GP16)
three_way_relay.direction = Direction.OUTPUT

door_button_relay = DigitalInOut(board.GP17)
door_button_relay.direction = Direction.OUTPUT

WAIT_TIME = 8

# TODO:
# * enforce sleep afted garage door is opened manually/wo the 3-way

states_actions = {
    #Prior          Now             Door    3-way
    #Door   Expect  Door  Expect    Button  Relay  Sleep
    (False, False, False, False):   (False, False, False),
    (False, False, False, True):    (True,  False, True),  # 3-way requested door action
    (False, False, True,  False):   (False, True,  True),  # Update 3-way to reflect door
    (False, False, True,  True):    (False, False, False), # n/a prv action
    (False, True,  False, False):   (False, False, False),
    (False, True,  False, True):    (False, True,  False), # Err on prev response to 3-way
    (False, True,  True,  True):    (False, False, False),
    (True,  False, False, False):   (False, False, False), # n/a prv action
    (True,  False, False, True):    (False, True,  False), # Rate limit 3-way actions
    (True,  False, True,  False):   (False, True,  False), # Err on prev response to 3-way
    (True,  False, True,  True):    (False, False, False),
    (True,  True,  False, False):   (False, False, False),
    (True,  True,  False, True):    (False, True,  False), # Update 3-way to reflect door
    (True,  True,  True,  False):   (True,  False, True),  # 3-way requested door action
    (True,  True,  True,  True):    (False, False, False)
}

now_door = door_is_open.value
now_expect = three_way_relay.value

while True:
    time.sleep(1)

    prior_door = now_door
    prior_expect = now_expect
    now_door = door_is_open.value
    now_expect = door_expected_open.value

    print('pd', prior_door, 'pe', prior_expect, 'nd', now_door, 'ne', now_expect)

    state = (prior_door, prior_expect, now_door, now_expect)
    push_door_button, toggle_relay, sleep_delay = states_actions[state]

    if push_door_button:
        print('Pushing the door button')
        door_button_relay.value = True
        time.sleep(0.1)
        door_button_relay.value = False
    
    if toggle_relay:
        print('Toggling the 3-way relay')
        three_way_relay.value = not three_way_relay.value

    if sleep_delay:
        print(f'Sleeping {WAIT_TIME} seconds')
        time.sleep(WAIT_TIME)






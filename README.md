# diy_garage_door_controller
For lack of a simple garage door controller to work with google home, this is an implementation using a smart 3-way switch, a few relays, and a pi pico microcontroller.

This setup should work with any smart 3-way switch that allows you to use a single smart switch in the 3-way circuit. E.g. the Kasa HS210 which is only about $15.  The cool thing about using a 3-way switch is that it can controll the door, and you can also toggle the relay attached to it to signal back that the door has been opened or closed.  So someone in the garage can open the door with their remote and the smart switch will turn "on" in its app to indicate that the door is open.  Or if you you use the smart switch to close the door, it will show as closed during the wait period, but report open again if it failed to close. 

On the garage door opener end of things, it would need to be the type that will open/close by shorting the pins of the opener that normally would go to a button in the garage.  Some newer units may not support this, but you could u connect this to a wireless remote as an alternative.

## Warning regarding 120vac electricity
This project uses 120v ac power and plugs into an outlet in the house.  120vac can kill you.  If you are shocked, it can put your heart into an arythmea and you can die hours later.  It can kill you in other ways.  I am not an electrician or an expert and you should not replicate anything I have posted here.  I am not responseble if you hurt yourself or others or burn your house down.  

That said, here are a few precautions I have implemented in this setup:
* Covering any pins or wires with 120v with hot glue, paper, and electrical tape to protect against accidental touches. 
* Securing all electronics in the enclosure.
* Using a properly grounded and gfci protected circuit to power it.
* Physical isolaton of 120vac and 5vdc electronics via relays.

## Circuit Diagram

## Required Features
* Garage door can be controlled from existing wireless controllers
* Opened/Closed state of the door should be shown in google home (or your smart home interface of choice)
* Should be able to press 3-way switch or toggle it in the app to open or close the door, and see the result in the app.  E.g. if I try to close it but after defined wait time it is open, toggle the relay attached to the 3-way to signal that the door is stil open. 

## Programming
The program that runs on the micro-controller needs to be simple enough to be certain that it will function as intended. The best way I came up with to do this it to make a list of previous and current states of the garage door and the three-way switch and the actions that should take place for all combinations of these states.  

I call the states 
* "prior_door" - Whether the door was open previously
* "prior_expected" - Whetehr the door was expected to be open previously
* "now_door" - Whether the door is open now
* "now_expected" - Whether the door is expected to be open now

And the resulting possible actions are:
* "push_door_button" - Closes and opens the relay connected to the garage door opener to tell it to open or close the door.
* "toggle_relay" - Alternates the state of the relay connected to the 3-way switch to signal to it a change in the state of the door
* "sleep_wait" - Simply sleeps for a few seconds. This is to wait for the door to move and rate limit actions initiated by the 3-way switch.

### State and Action Table:
```
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
```

We have a few lines to initialize all of the needed GPIO Pins and set our WAIT_TIME. The wait time should be a little longer than it takes for your garage door to open or close.

```import board
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

WAIT_TIME = 5
```

And The main loop is pretty simple.  Print statements are for debugging over serial on initial wire-up.
```
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
```

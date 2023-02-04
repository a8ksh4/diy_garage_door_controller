# diy_garage_door_controller
For lack of a simple garage door controller to work with google home, this is an implementation using a smart 3-way switch, a few relays, and a pi pico microcontroller.

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

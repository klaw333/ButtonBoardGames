import RPi.GPIO as GPIO
import time
import numpy
from datetime import datetime
import random
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#setup LEDs
led_list = [14,15,18,23,24,25,8,7,1,12,16,20]
for led in led_list:
    GPIO.setup(led,GPIO.OUT)

#setup buttons. Some buttons are wired different than others.
button_down_list = [2,3]
for buttons in button_down_list:
    GPIO.setup(buttons, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
button_up_list = [4,17,27,10,9,11,5,6,21,0]
for buttons in button_up_list:
    GPIO.setup(buttons, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#lightning_game turns on LEDs and the player needs to hit the buttons before the time runs out
def lightning_game():
    class button:
        def __init__(self, timer, timer_start, number):
            self.timer = 0
            self.timer_start = time.time()
            self.number = 0
    countdown_animation()
    button_a = button(0, time.time(), 0)
    button_b = button(0, time.time(), 0)
    button_targets = [button_a, button_b]
    button_a.number = get_random_button(button_targets)
    button_b.number = get_random_button(button_targets)
    time_limit = 3
    level_score = 0
    level = 1
    miss_limit = 2
    miss_count = 0
    time_reduction_rate = .90
    #hard mode -shorter time limits, third button, lower miss limit
    if is_button_pushed(27) and is_button_pushed(4):
        miss_limit = 3
        time_limit = 1.5
        time_reduction_rate = .87
        flash_button_list = [27,4]
        button_c = button(0, time.time(), 0)
        button_c.number = get_random_button(button_targets)
        button_targets.append(button_c)
        flash_buttons(5, flash_button_list)

    #initialize buttons
    for button in button_targets:
        turn_led_on(button.number)
        button.timer_start = time.time()

    #running lightning game
    while True:
        for target_button in button_targets:
            if is_button_pushed(target_button.number):
                turn_led_off(target_button.number)
                target_button.number = get_random_button(button_targets)
                turn_led_on(target_button.number)
                target_button.timer_start = time.time()
                level_score += 1
            elif target_button.timer > time_limit and miss_count < miss_limit:
                miss_count += 1
                turn_led_off(target_button.number)
                target_button.number = get_random_button(button_targets)
                turn_led_on(target_button.number)
                target_button.timer_start = time.time()
            elif target_button.timer > time_limit and miss_count >= miss_limit:
                turn_off_all_leds()
                blink_missed_button(target_button.number)
                turn_off_all_leds()
                return
            target_button.timer = time.time() - target_button.timer_start
            
        if level_score > 40:
            level += 1
            level_transition_animations(level)
            level_score = 0
            miss_count = 0
            time_limit = time_limit * time_reduction_rate
            for button in button_targets:
                button.number = get_random_button(button_targets)
                turn_led_on(button.number)
                button.timer_start = time.time()

#memory_game shows a pattern of LEDs and the player needs to repeat the pattern with button presses 
def memory_game():
    wipe_animation()
    pattern = [get_random_button()]
    level = 1
    time.sleep(1)
    button_pushed = False
    time_limit = 45
    last_required_button = -1
    for i in range(100):
        pattern.append(get_random_button([pattern[-1]]))
    show_button_pattern(pattern[0:level+2])
    #running memory game
    while True:
        for required_button in pattern[0:level+2]:
            button_pushed = what_button_is_pressed(time_limit, [last_required_button])
            if button_pushed == required_button:
                turn_led_on(required_button)
                last_required_button = required_button
            else:
                blink_missed_button(required_button)
                turn_off_all_leds()
                return
        turn_led_on(required_button)
        time.sleep(.05)
        congrats_animation(1.2)
        level += 1
        show_button_pattern(pattern[0:level+2])

#loop_game cycles the LEDs on the outer ring and the player has to press the red button when it's lit up.
def loop_game():   
    loop_animation(4)
    turn_off_all_leds()
    outter_button_list = [21,2,9,17,6,0,11,10,27]
    speed = .50
    level = 1
    timer = 0
    timer_start = time.time()
    for i in range(30):
        for button in outter_button_list:
            turn_led_on(button)
            timer_start = time.time()
            timer = 0
            while timer < speed:
                timer = time.time() - timer_start
                if is_button_pushed(27):
                    if button == 27:
                        congrats_animation(1.25)
                        level += 1
                        speed = speed * .9
                        level_display(level)
                    else:
                        blink_missed_button(button)
                        turn_off_all_leds()
                        return
            turn_led_off(button)


def what_button_is_pressed(watch_time_limit,exclude = []):
    button_list = [21,2,9,17,27,4,3,5,10,11,0,6]
    timer = 0
    timer_start = time.time()
    while timer < watch_time_limit:
        timer = time.time() - timer_start
        for button in button_list:
            if is_button_pushed(button) and button not in exclude:
                while is_button_pushed(button):
                    time.sleep(.08)
                time.sleep(.12)
                return button
    return "timeout"

def show_button_pattern(pattern = []):
    turn_off_all_leds()
    for button in pattern:
        turn_led_on(button)
        time.sleep(1.5)
        turn_led_off(button)
    
def level_transition_animations(level):
    congrats_animation()
    level_display(level)
    countdown_animation()
    
def congrats_animation(time_limit = 3):
    turn_off_all_leds()
    timer_start = 0
    timer = 0
    timer_start = time.time()
    x = 0
    while timer <= time_limit:
        button = get_random_button()
        turn_led_on(button)
        time.sleep(.05)
        turn_led_off(button)
        x+=1
        timer = time.time() - timer_start
    turn_off_all_leds()
    
def level_display(level):
    turn_off_all_leds()
    x=0
    mod_level = level % 12
    button_list = [21,2,9,17,27,4,3,5,10,11,0,6]
    for button in button_list:
        if x >= mod_level:
            break
        turn_led_on(button)
        x+=1
    time.sleep(2)
    turn_off_all_leds()
    
def countdown_animation():
    button_list = [21,2,9,17,27,4,3,5,10,11,0,6]
    turn_on_all_leds()
    for button in button_list:
        turn_led_off(button)
        time.sleep(.22)
        
def flash_buttons(flash_times, button_list = []):
    for x in range(flash_times):
        for button in button_list:
            turn_led_off(button)
            time.sleep(.1)
            turn_led_on(button)
            time.sleep(.1)
    turn_off_all_leds()

def turn_off_all_leds():
    led_list = [14,15,18,23,24,25,8,7,1,12,16,20]
    for led in led_list:
        GPIO.output(led,GPIO.LOW)

def turn_on_all_leds():
    led_list = [14,15,18,23,24,25,8,7,1,12,16,20]
    for led in led_list:
        GPIO.output(led,GPIO.HIGH)

def get_random_button(used_buttons = []):
    button_list = [27,21,4,10,11,2,3,0,9,5,17,6]
    if len(used_buttons) > 0:
        for button in used_buttons:
            if type(button) == int:
                if button in button_list:
                    button_list.remove(button)
            else:
                if button.number in button_list:
                    button_list.remove(button.number)
    new_random_button_number = (random.choice(button_list))
    return new_random_button_number

def turn_led_off(button_number):
    led_number = convert_button_to_led(button_number)
    GPIO.output(led_number,GPIO.LOW)

def turn_led_on(button_number):
    led_number = convert_button_to_led(button_number)
    GPIO.output(led_number,GPIO.HIGH)

def convert_button_to_led(button_number):
    button_x_led = {
                    27:25, 
                    21:23, 
                    4:18,
                    10:8,
                    11:14,
                    2:15,
                    3:24,
                    0:7,
                    9:1,
                    5:12,
                    17:20,
                    6:16}
    led_number = button_x_led[button_number]
    return led_number
    
def is_button_pushed(button_number):
    if GPIO.input(button_number) == GPIO.LOW:
        return True
    else:
        return False

#blink provided button
def blink_missed_button(button_number):
    for x in range(20):
        turn_led_off(button_number)
        time.sleep(.1)
        turn_led_on(button_number)
        time.sleep(.1)

#cycles LEDs from left to right
def wipe_animation():
    speed = .10
    turn_off_all_leds()
    turn_led_on(27)
    time.sleep(speed)
    turn_led_off(27)
    time.sleep(speed)
    turn_led_on(21)
    turn_led_on(10)
    time.sleep(speed)
    turn_led_off(21)
    turn_led_off(10)
    time.sleep(speed)
    turn_led_on(4)
    time.sleep(speed)
    turn_led_off(4)
    time.sleep(speed)
    turn_led_on(2)
    turn_led_on(11)
    time.sleep(speed)
    turn_led_off(2)
    turn_led_off(11)
    time.sleep(speed)
    turn_led_on(3)
    time.sleep(speed)
    turn_led_off(3)
    time.sleep(speed)
    turn_led_on(0)
    turn_led_on(9)
    time.sleep(speed)
    turn_led_off(0)
    turn_led_off(9)
    time.sleep(speed)
    turn_led_on(5)
    time.sleep(speed)
    turn_led_off(5)
    time.sleep(speed)
    turn_led_on(17)
    turn_led_on(6)
    time.sleep(speed)
    turn_led_off(17)
    turn_led_off(6)

#turns on all LEDs and turns them off when the player presses the button so lights and buttons can be tested
def diagnostics():
    turn_on_all_leds()
    time.sleep(2)
    turn_off_all_leds()
    time.sleep(2)
    turn_on_all_leds()
    button_list = [27,21,4,10,11,2,3,0,9,5,17,6]
    while True:
        for button in button_list:
            if is_button_pushed(button):
                turn_led_off(button)
                button_list.remove(button)
        if len(button_list) == 0:
            return

#cycles outer ring of LEDs in clockwise direction 
def loop_animation(loops):
    outter_button_list = [27,21,2,9,17,6,0,11,10]
    loop_count = 0
    turn_led_on(4)
    turn_led_on(5)
    turn_led_on(3)
    while loop_count < loops:
        for button in outter_button_list:
            turn_led_on(button)
            time.sleep(.05)
            turn_led_off(button)
        loop_count += 1
    turn_off_all_leds()

#main_menu is where the payer can select a game to play. While waiting for the player to select a game a random LED will turn if the player presses that button it will off and a new LED will light up. This is an idle mini game.
def main_menu():
    turn_off_all_leds()
    button = get_random_button()
    turn_led_on(button)
    diagnostics_timer_start = 0
    diagnostics_timer = 0
    lightning_game_timer_start = 0
    lightning_game_timer = 0
    loop_game_timer_start = 0
    loop_game_timer = 0
    memory_game_timer_start = 0
    memory_game_timer = 0
    while True:
        if is_button_pushed(button):
            turn_led_off(button)
            button = get_random_button([button])
            turn_led_on(button)
            
        if is_button_pushed(27): #red button is 27
            if lightning_game_timer == 0:
                lightning_game_timer_start = time.time()
            lightning_game_timer = time.time() - lightning_game_timer_start
            if lightning_game_timer > 1:
                lightning_game()
                turn_led_on(button)
        else:
            lightning_game_timer = 0
        
        if is_button_pushed(2) and is_button_pushed(21):
            if memory_game_timer == 0:
                memory_game_timer_start = time.time()
            memory_game_timer = time.time() - memory_game_timer_start
            if memory_game_timer > 1:
                memory_game()
                turn_led_on(button)
        else:
            memory_game_timer = 0
                
        if is_button_pushed(17) and is_button_pushed(10): #bottom left and uppe right buttons
            if diagnostics_timer == 0:
                diagnostics_timer_start = time.time()
            diagnostics_timer = time.time() - diagnostics_timer_start
            if diagnostics_timer > 4:
                diagnostics()
                turn_led_on(button)
        else:
            diagnostics_timer = 0
                        
        if is_button_pushed(11) and is_button_pushed(10): 
            if loop_timer == 0:
                loop_timer_start = time.time()
            loop_timer = time.time() - loop_timer_start
            if loop_timer > 1:
                loop_game()
                turn_led_on(button)
        else:
            loop_timer = 0
            
main_menu()

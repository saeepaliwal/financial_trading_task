# -*- coding: utf-8 -*-    
from __future__ import division
from choice_task import ChoiceTask
import pygame
from pygame.locals import *
from trading_task_functions import *
import random
import numpy as np
import trading_buttons
import pdb
from scipy.io import savemat
import platform

testing = True

training = False

response_box = True
currency = 'points'

# Initialize response box:
if response_box: 
    if platform.system() == 'Darwin': # Mac
        RTB = serial.Serial(baudrate=115200, port='/dev/tty.usbserial-142', timeout=0)
    elif platform.system() == 'Windows': # Windows
        RTB = serial.Serial(baudrate=115200, port='COM4', timeout=0)

# Define special characters
ae = u"ä";
ue = u"ü";

# Define colors:
BLUE =   (  0,   0, 128)
GREEN =  (  0, 100,   0)
RED =    (178,  34,  34)
YELLOW = (255, 215,   0)
GRAY =   (139, 139, 131)
PURPLE = ( 72,  61, 139)
ORANGE = (255, 140,   0)
WHITE =  (255, 255, 255)
DARK_GRAY = ( 20, 20, 20)
GOLD   = ( 254, 195,  13)
BLACK  = (   0,   0,   0)

background_music = []
background_music.append(pygame.mixer.Sound('./sounds/ticker1_music.wav'))
background_music.append(pygame.mixer.Sound('./sounds/ticker2_music.wav'))
background_music.append(pygame.mixer.Sound('./sounds/ticker1_music.wav'))
background_music.append(pygame.mixer.Sound('./sounds/ticker2_music.wav'))
for i in range(4):
    background_music[i].set_volume(0.1)

c = ChoiceTask(background_color=BLACK, 
    title  = pygame.font.Font('./fonts/SansSerifFLF.otf', 40),
    body  = pygame.font.Font('./fonts/Oswald-Bold.ttf', 30),
    header = pygame.font.Font('./fonts/SansSerifFLF.otf', 40),
    instruction = pygame.font.Font('./fonts/GenBasR.ttf',30),
    choice_text = pygame.font.Font('./fonts/GenBasR.ttf', 30),
    button = pygame.font.Font('./fonts/SansSerifFLF.otf',30))

(subjectname) = c.subject_information_screen()
subject = subjectname.replace(" ","")
matlab_output_file = c.create_output_file(subjectname)
c.blank_screen()

result_sequence = []
wheel_hold_bool = [True, False]
block_order = []
control_seq = []

# Define open prices for the four stocks
open_prices = [20, 40, 60, 80]

# Pull in training trials:
with open ('./traces/taskBackend_training.txt','r') as f:
        probability_trace = f.read().replace('\n', '')
result_sequence = probability_trace.split(',')

# Randomize blocks for real trials
block_order = [1,2,3,4]
random.shuffle(block_order)

for b in block_order:
    with open ('./traces/taskBackend_' + str(b) + '.txt','r') as f:
        probability_trace = f.read().replace('\n', '')
    block_sequence = probability_trace.split(',')
    if block_sequence[0] == 'CONTROL':
        wheel_hold_bool.append(True)
        control_seq.append(1)
    elif block_sequence[0] == 'NOCONTROL':
        wheel_hold_bool.append(False)
        control_seq.append(0)
    block_sequence = block_sequence[1:]
    result_sequence = result_sequence + block_sequence
    print "Block sequence: " + str(b)

# Set trial switch specifications
if testing:
    NUM_TRIALS = 30
    task_block_sequence=[10,20,22,24,26,28]
else:     
    NUM_TRIALS = len(result_sequence)-1
    task_block_sequence=[10,20,50,80,110,140]


# Define dictionary of task attributes:
task = {'trade_size': np.zeros(NUM_TRIALS).astype('int'),
        'account': np.zeros(NUM_TRIALS).astype('int'),
        'result_sequence': result_sequence,
        'stock_sequence': np.zeros(NUM_TRIALS).astype('int'),
        'reward_grade': np.zeros(NUM_TRIALS).astype('int'),
        'winloss': np.zeros(NUM_TRIALS).astype('int'),
        'pressed_stop': np.zeros(NUM_TRIALS).astype('int'),
        'guess_trace': np.zeros(NUM_TRIALS).astype('int'),
        'current_price':np.zeros(NUM_TRIALS).astype('int'),
        }

# Start with initial account and stock
task['stock'] = 0

task['block_order'] = block_order
task['control_seq'] = control_seq
task['trial_stage'] = 'guess'

# Training trials
task['num_training_trials'] = task_block_sequence[1]

# Times
task['inter_wheel_interval'] = 700
task['win_banner_interval'] = 1500
task['win_screen_interval'] = 1500

# Individual wheel hold buttons:
task['wheel_hold_buttons'] = wheel_hold_bool[0]
task['wheel1'] = False
task['wheel2'] = False
task['wheel3'] = False

if training:
    task['training'] = True
    START_TRIAL = 0
    task['account'][START_TRIAL] = 500
    task['current_price'][START_TRIAL] = open_prices[1]
else:
    task['training'] = False
    START_TRIAL = 20
    task['account'][START_TRIAL] = 2000

# Set up initial screen 
positions, buttons, sizes = get_screen_elements(c, task)

if training:
    welcome_screen(c)
    instruction_screen(c,positions,sizes,RTB)

for trial in range(START_TRIAL,NUM_TRIALS): 
    next_trial = False    

    print trial
    if trial == 0:
        begin_training_screen(c)
        background_music.play(100,0)
    if trial < task_block_sequence[0]:
        task['stock'] = 0
        task['wheel_hold_buttons'] = wheel_hold_bool[0]
    elif task_block_sequence[0] <= trial < task_block_sequence[1]:
        task['stock'] = 1
        task['wheel_hold_buttons'] = wheel_hold_bool[1]
    elif trial == task_block_sequence[1]:
        if training:
            task['training'] = False
            background_music[0].stop()
            end_training_screen(c)
        task['account'][trial] = 2000
        task['current_price'][trial] = open_prices[task['stock']]
        task['current_price'][trial-1] = open_prices[task['stock']]
        task['stock'] = block_order[0]-1
        task['current_block'] = block_order[0]
        task['wheel_hold_buttons'] = wheel_hold_bool[2]
        #welcome_screen(c)
        background_music[0].play(100,0)
        c.log('Starting block ' + str(block_order[0]) + ' at ' + repr(time.time()) + '\n')
        c.log('Stock ' + str(task['stock']) + 'at ' + repr(time.time()) + '\n')
        c.log('Wheel hold buttons are ' + str(wheel_hold_bool[3]) + ' at ' + repr(time.time()) + '\n')
    elif trial == task_block_sequence[2]:
        background_music[0].stop()
        change_machine_screen(c)
        task['stock'] = block_order[1]-1
        task['current_block'] = block_order[1]
        task['wheel_hold_buttons'] = wheel_hold_bool[3]
        c.log('Starting block ' + str(block_order[1]) + ' at ' + repr(time.time()) + '\n')
        c.log('Machine ' + str(task['stock']) + ' at ' + repr(time.time()) + '\n')
        c.log('Wheel hold buttons are ' + str(wheel_hold_bool[2]) + ' at ' + repr(time.time()) + '\n')
        background_music[1].play(100,0)
    elif trial == task_block_sequence[3]:
        background_music[1].stop()
        change_machine_screen(c)
        task['stock'] = block_order[2]-1
        task['current_block'] = block_order[2]
        task['wheel_hold_buttons'] = wheel_hold_bool[4]
        c.log('Starting block ' + str(block_order[2]) + ' at ' + repr(time.time()) + '\n')
        c.log('Stock ' + str(task['stock']) + 'at ' + repr(time.time()) + '\n')
        c.log('Wheel hold buttons are ' + str(wheel_hold_bool[3]) + ' at ' + repr(time.time()) + '\n')
        background_music[2].play(100,0)
    elif trial == task_block_sequence[4]:
        background_music[2].stop()
        change_machine_screen(c)
        task['stock'] = block_order[3]-1
        task['current_block'] = block_order[3]
        task['wheel_hold_buttons'] = wheel_hold_bool[5]
        c.log('Starting block ' + str(block_order[3]) + ' at ' + repr(time.time()) + '\n')
        c.log('Stock ' + str(task['stock']) + 'at ' + repr(time.time()) + '\n')
        c.log('Wheel hold buttons are ' + str(wheel_hold_bool[5]) + ' at ' + repr(time.time()) + '\n')
        background_music[3].play(100,0)

    task['trade_sequence'] = []
    task['trial'] = trial

    
    task['ungrey_wheel2'] = False
    task['ungrey_wheel3'] = False
    task['stock_sequence'][trial] = task['stock']

    # Set stage and selector
    task['trial_stage'] = 'guess'
    selector_pos = 1

    if trial > 0 and training:
        task['account'][trial] = task['account'][trial-1] 
    elif trial > 20 and not training:
        task['account'][trial] = task['account'][trial-1] 

    task['reward_grade'][trial] = int(str(result_sequence[trial])[1])

    buttons, task = draw_screen(c, positions, buttons, sizes, task)
    selector_pos, selected = selector(c,task,positions,0,selector_pos)


    # EEG: Guess on
    eeg_trigger(c,task,'guess_on')

    while not next_trial:   
        pygame.time.wait(20)

        key_press = RTB.read() 
        if len(key_press):
            key_index = ord(key_press)

            if task['trial_stage'] == 'guess':
                selected = False
                draw_screen(c, positions, buttons, sizes, task)
                selector_pos, selected = selector(c,task,positions,key_index,selector_pos)
                if selected:              
                    eeg_trigger(c,task,'pressed_guess')
                    task['guess_trace'][trial] = selector_pos
                    task['trial_stage'] = 'bet'
                    buttons, task = draw_screen(c, positions, buttons, sizes, task)
            elif task['trial_stage'] != 'guess':
                events = process_rtb(positions,key_index, task['trial_stage'], task['wheel_hold_buttons'])
                if len(events) > 0:
                    pygame.event.post(events[0])
                    pygame.event.post(events[1])

        for event in pygame.event.get():
            if event.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                if 'click' in buttons['add_five'].handleEvent(event): 
                    c.press_sound.play()
                    task['trial_stage'] = 'bet'
                    task['trade_size'][trial] += 5
                    task['trade_sequence'].append(5)
                    eeg_trigger(c,task,'bet+')
                    task = update_account(c,positions, sizes, task)
                    display_assets(c,positions,sizes,task)
                    c.log('Trial ' + str(trial) + ': Added shares to trade. ' + repr(time.time()) + '\n')
                elif 'click' in buttons['clear'].handleEvent(event):
                    c.press_sound.play()
                    if len(task['trade_sequence']) > 0:   
                        c.log('Trial ' + str(trial) + ': Clearing ' + str(task['trade_sequence'][-1]) + 'from trade. ' + repr(time.time()) + '\n')
                        task['trial_stage'] = 'clear'
                        eeg_trigger(c,task,'bet-')
                        task = clear(c,task)
                        task = update_account(c,positions, sizes, task)
                        display_assets(c,positions,sizes,task)
                elif 'click' in buttons['place_order'].handleEvent(event):
                    if task['trade_size'][trial] > 0:
                        c.press_sound.play()
                        task['trial_stage'] = 'pull'
                        buttons, task = draw_screen(c, positions, buttons, sizes, task)
                        buttons['place_order'].draw(c.screen)
                        eeg_trigger(c,task,'pressed_pull')
                        pygame.display.update()
                        c.log('Trial ' + str(trial) + ': Pulling wheels ' + repr(time.time()) + '\n')
                        c.log('Summary Trial' + str(trial) + ': Trade:' + str(task['trade_size'][trial]) + 'Account: ' + str([task['account'][trial]]))
                        task['trial_stage'] = 'result'
                        if task['wheel_hold_buttons']:
                            individual_price_spin(c,positions,buttons,sizes,task, RTB)
                        else:
                            spin_prices(c, positions, buttons, task)
                            show_result(c,positions,buttons,task)

                        task = process_result(c,positions,buttons,sizes,task, RTB) 
                        next_trial = True
            elif event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
        
            if not next_trial:
                for key in buttons:
                    buttons[key].draw(c.screen)
            pygame.display.update()

            savemat(matlab_output_file,task)
  
savemat(matlab_output_file,task)    
background_music[3].stop()  
c.exit_screen("That ends the game! Thank you so much for playing! Goodbye!", font=c.title, font_color=GOLD)


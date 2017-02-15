# TimeBuddy

(Insert product image here)

## TimeBuddy consists of 2 parts
1. A flask project hosting a web UI and restful API 
2. The TimeBuddy program.

For documentation on either of these parts see the README in their respective 
folders (Coming soon!)

### Project Background
TimeBuddy is built as a part of a school project, the given subject is 
"On the Edge of Time", the general theme is that time is a shrinking commodity 
and our task is to create a product that can somehow alleviate that. 

Considering how it's impossible to increase the amount of time available we 
quickly agreed that a product that helps one increase productivity was the way 
to go an we then started to develop the idea behind TimeBuddy.

Having recently read about the Pomodoro Technique we wanted this to be the 
core idea in TimeBuddy.

### Core Idea

The idea of TimeBuddy is really two things:

1. A Pomodoro timer
2. An activity tracker

Each idea will be further described in greater detail by its own.
 
But since this project basically needs to do two things it's build as a basis 
platform with hardware wise a 16x2 LCD screen, two LEDs and a buzzer for output and 
four buttons (start, stop, back, forward) for input. 
Software wise TimeBuddy is just a simple program which initializes the 
input and output, then creates the different program objects with said 
input/output and then runs the program objects main method, but this is 
explained in greater detail in the TimeBuddy README file.

### Pomodoro Timer
#### Description of the Pomodoro Technique from wikipedia (15/2 - 17)
The Pomodoro Technique is a time management method developed by Francesco Cirillo in the late 1980s. The technique uses a timer to break down work into intervals, traditionally 25 minutes in length, separated by short breaks. These intervals are named pomodoros, the plural in English of the Italian word pomodoro (tomato), after the tomato-shaped kitchen timer that Cirillo used as a university student.

##### TL;DR
The Pomodoro Technique is:

1. Select a task
1. Start a 25 minute timer
2. Work on said task
3. When the timer rings
    * Make a mark
    * Stop working
    * Start a 5 minute timer
5. Have a break
6. When the break timer rings go to step 2
7. Once you have 4 marks
    * Have a longer break (30 minutes)
    * Go to step 2

##### How it helps
This technique helps your productivity since it:
* Forces you to actively decide what task to accomplish
* Gives you small breaks for reflection 
* Gives you longer breaks, this feels both feels like a reward, but also keeps you
from burning out

###Activity Tracker
Activity tracker might seem like something out of some creepy sci-fi show 
but sometimes it's nice to know how much time you spent on certain activities, 
especially if you're trying to optimize your time. 

And activity tracker does just that, when starting an Activity Tracker session 
you will be asked to choose an activity from your list of activities, once the 
timer is stopped the time spent on the activity will be logged in a database 
on the restful API.

The web UI is used to manage your list of tasks.

Activity Tracker also bleeds into the Pomodoro timer, and every pomodoro 
session is logged as well.


# Dependencies
* Flask
* requests
* google-api-python-client
* RPi.GPIO
* sqlite3
* json
* threading
#!/usr/bin/env python

import robot_api
import rospy
import sys, select, termios, tty

msg = """
Control Your Fetch!
---------------------------
Moving around:
        w
   a    s    d

Space: force stop
i/k: increase/decrease only linear speed by 5 cm/s
u/j: increase/decrease only angular speed by 0.25 rads/s
anything else: stop smoothly

CTRL-C to quit
"""

moveBindings = {'w': (1, 0), 'a': (0, 1), 'd': (0, -1), 's': (-1, 0)}
speedBindings = {
    'i': (0.05, 0),
    'k': (-0.05, 0),
    'u': (0, 0.25),
    'j': (0, -0.25),
}

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

speed = 0.2
turn = 1.0

def vels(speed, turn):
    return f"currently:\tspeed {speed:.2f}\tturn {turn:.2f}"

if __name__ == "__main__":
    settings = termios.tcgetattr(sys.stdin)
    rospy.init_node('fetch_teleop_key')
    base = robot_api.Base()

    x = 0
    th = 0
    status = 0
    count = 0
    target_speed = 0
    target_turn = 0
    control_speed = 0
    control_turn = 0
    last_print = ""

    try:
        print(msg)
        print(vels(speed, turn))
        while not rospy.is_shutdown():
            key = getKey()
            if key in moveBindings:
                x, th = moveBindings[key]
                count = 0
            elif key in speedBindings:
                speed += speedBindings[key][0]
                turn += speedBindings[key][1]
                print(vels(speed, turn))
                count = 0
            elif key == ' ':
                x = 0
                th = 0
                control_speed = 0
                control_turn = 0
            else:
                count += 1
                if count > 4:
                    x = 0
                    th = 0
                if key == '\x03':
                    break

            target_speed = speed * x
            target_turn = turn * th

            if target_speed > control_speed:
                control_speed = min(target_speed, control_speed + 0.02)
            elif target_speed < control_speed:
                control_speed = max(target_speed, control_speed - 0.02)
            else:
                control_speed = target_speed

            if target_turn > control_turn:
                control_turn = min(target_turn, control_turn + 0.1)
            elif target_turn < control_turn:
                control_turn = max(target_turn, control_turn - 0.1)
            else:
                control_turn = target_turn

            base.move(control_speed, control_turn)

    except Exception as e:
        rospy.logerr(str(e))

    finally:
        base.stop()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

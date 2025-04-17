#!/usr/bin/env python

import math
import robot_api
import rospy


def wait_for_time():
    while rospy.Time().now().to_sec() == 0:
        pass

def print_usage():
    print('Usage: rosrun applications base_demo.py move 0.5')
    print('       rosrun applications base_demo.py rotate 30')

def main():
    rospy.init_node('base_demo')
    wait_for_time()
    argv = rospy.myargv()
    if len(argv) < 3:
        print_usage()
        return

    command = argv[1]
    value = float(argv[2])
    base = robot_api.Base()

    if command == 'move':
        base.go_forward(value)
    elif command == 'rotate':
        base.turn(math.radians(value))
    else:
        print_usage()

if __name__ == '__main__':
    main()

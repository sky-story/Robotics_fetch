#!/usr/bin/env python

import rospy
from joint_state_reader import JointStateReader

def wait_for_time():
    while rospy.Time().now().to_sec() == 0:
        pass

def main():
    rospy.init_node('joint_reader_demo')
    wait_for_time()
    reader = JointStateReader()
    rospy.sleep(0.5)

    names = [
        'shoulder_pan_joint',
        'shoulder_lift_joint',
        'upperarm_roll_joint',
        'elbow_flex_joint',
        'forearm_roll_joint',
        'wrist_flex_joint',
        'wrist_roll_joint',
        'l_gripper_finger_joint',
        'torso_lift_joint'
    ]

    values = reader.get_joints(names)
    for name, value in zip(names, values):
        print(f"{name}\t{value}")

if __name__ == '__main__':
    main()

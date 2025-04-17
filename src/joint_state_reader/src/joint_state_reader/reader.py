#!/usr/bin/env python

import rospy
from sensor_msgs.msg import JointState
from threading import Lock

class JointStateReader(object):
    def __init__(self):
        self.joint_values = {}
        self.lock = Lock()
        rospy.Subscriber('/joint_states', JointState, self.joint_callback)

    def joint_callback(self, msg):
        with self.lock:
            for name, position in zip(msg.name, msg.position):
                self.joint_values[name] = position

    def get_joint(self, name):
        with self.lock:
            return self.joint_values.get(name, None)

    def get_joints(self, names):
        with self.lock:
            return [self.joint_values.get(name, None) for name in names]

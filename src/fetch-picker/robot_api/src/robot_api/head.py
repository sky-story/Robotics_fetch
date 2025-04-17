#!/usr/bin/env python3

import math
import rospy
import actionlib
from trajectory_msgs.msg import JointTrajectoryPoint, JointTrajectory
from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal
from control_msgs.msg import PointHeadAction, PointHeadGoal
from geometry_msgs.msg import PointStamped

LOOK_AT_ACTION_NAME = '/head_controller/point_head'
PAN_TILT_ACTION_NAME = '/head_controller/follow_joint_trajectory'
PAN_JOINT = 'head_pan_joint'
TILT_JOINT = 'head_tilt_joint'
PAN_TILT_TIME = 2.5  # seconds

class Head(object):
    """Head controls the Fetch's head via pan/tilt or look_at interfaces."""

    MIN_PAN = -1.57
    MAX_PAN = 1.57
    MIN_TILT = -0.76
    MAX_TILT = 1.45

    def __init__(self):
        self._point_head_client = actionlib.SimpleActionClient(LOOK_AT_ACTION_NAME, PointHeadAction)
        self._pan_tilt_client = actionlib.SimpleActionClient(PAN_TILT_ACTION_NAME, FollowJointTrajectoryAction)

        rospy.loginfo("Waiting for head servers...")
        self._point_head_client.wait_for_server()
        self._pan_tilt_client.wait_for_server()
        rospy.loginfo("Head action servers connected.")

    def look_at(self, frame_id, x, y, z):
        goal = PointHeadGoal()
        goal.target.header.frame_id = frame_id
        goal.target.point.x = x
        goal.target.point.y = y
        goal.target.point.z = z
        goal.min_duration = rospy.Duration(1.0)

        self._point_head_client.send_goal(goal)
        self._point_head_client.wait_for_result()
        rospy.loginfo("Looked at target point.")

    def pan_tilt(self, pan, tilt):
        if pan < self.MIN_PAN or pan > self.MAX_PAN or tilt < self.MIN_TILT or tilt > self.MAX_TILT:
            rospy.logwarn("Pan or tilt value is out of bounds.")
            return

        point = JointTrajectoryPoint()
        point.positions = [pan, tilt]
        point.time_from_start = rospy.Duration(PAN_TILT_TIME)

        goal = FollowJointTrajectoryGoal()
        goal.trajectory.joint_names = [PAN_JOINT, TILT_JOINT]
        goal.trajectory.points = [point]

        self._pan_tilt_client.send_goal(goal)
        self._pan_tilt_client.wait_for_result()
        rospy.loginfo(f"Head moved to pan={pan:.2f}, tilt={tilt:.2f}")


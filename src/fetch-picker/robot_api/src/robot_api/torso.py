#!/usr/bin/env python3

import rospy
import actionlib
from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal
from trajectory_msgs.msg import JointTrajectoryPoint

# Torso 控制器名称
ACTION_NAME = '/torso_controller/follow_joint_trajectory'
JOINT_NAME = 'torso_lift_joint'

TIME_FROM_START = 5  # seconds


class Torso(object):
    """Torso controls the robot's torso height."""
    MIN_HEIGHT = 0.0
    MAX_HEIGHT = 0.4

    def __init__(self):
        # 创建 actionlib 客户端
        self._client = actionlib.SimpleActionClient(ACTION_NAME, FollowJointTrajectoryAction)
        rospy.loginfo(f"Waiting for torso action server [{ACTION_NAME}]...")
        self._client.wait_for_server()
        rospy.loginfo("Torso action server connected!")

    def set_height(self, height):
        """Sets the torso height to a value between 0.0 and 0.4 meters."""

        # 检查高度是否合法
        if height < self.MIN_HEIGHT or height > self.MAX_HEIGHT:
            rospy.logwarn(f"Height {height} is out of bounds! Clipping to valid range.")
            height = max(min(height, self.MAX_HEIGHT), self.MIN_HEIGHT)

        # 创建轨迹点
        point = JointTrajectoryPoint()
        point.positions = [height]
        point.time_from_start = rospy.Duration(TIME_FROM_START)

        # 创建控制目标
        goal = FollowJointTrajectoryGoal()
        goal.trajectory.joint_names = [JOINT_NAME]
        goal.trajectory.points = [point]

        # 发送目标并等待结果
        self._client.send_goal(goal)
        self._client.wait_for_result()
        rospy.loginfo(f"Torso height set to {height}m.")


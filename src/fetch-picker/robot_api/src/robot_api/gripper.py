#!/usr/bin/env python3

import rospy
import actionlib
from control_msgs.msg import GripperCommandAction, GripperCommandGoal

# 控制接口名称（Fetch 官方文档给出）
ACTION_NAME = '/gripper_controller/gripper_action'

CLOSED_POS = 0.0   # Fully closed
OPENED_POS = 0.10  # Fully open (meters)


class Gripper(object):
    """Gripper controls the robot's gripper."""

    MIN_EFFORT = 35
    MAX_EFFORT = 100

    def __init__(self):
        # 创建 actionlib 客户端，连接到抓手控制器
        self._client = actionlib.SimpleActionClient(ACTION_NAME, GripperCommandAction)
        rospy.loginfo(f"Waiting for gripper action server [{ACTION_NAME}]...")
        self._client.wait_for_server()
        rospy.loginfo("Gripper action server connected!")

    def open(self):
        """Opens the gripper."""
        goal = GripperCommandGoal()
        goal.command.position = OPENED_POS
        goal.command.max_effort = self.MAX_EFFORT  # 控制打开时的最大力度
        self._client.send_goal(goal)
        self._client.wait_for_result()
        rospy.loginfo("Gripper opened.")

    def close(self, max_effort=MAX_EFFORT):
        """Closes the gripper."""
        if max_effort < self.MIN_EFFORT:
            max_effort = self.MIN_EFFORT  # 防止过小力度

        goal = GripperCommandGoal()
        goal.command.position = CLOSED_POS
        goal.command.max_effort = max_effort
        self._client.send_goal(goal)
        self._client.wait_for_result()
        rospy.loginfo("Gripper closed.")


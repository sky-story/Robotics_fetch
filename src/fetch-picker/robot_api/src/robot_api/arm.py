#!/usr/bin/env python3

# TODO: import actionlib
# TODO: import control_msgs.msg
# TODO: import trajectory_msgs.msg
import rospy
import actionlib
from trajectory_msgs.msg import JointTrajectoryPoint, JointTrajectory
from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal

from .arm_joints import ArmJoints

ARM_ACTION_NAME = '/arm_controller/follow_joint_trajectory'
TRAJECTORY_DURATION = 5.0  # seconds


class Arm(object):
    """Arm controls the robot's arm.

    Joint space control:
        joints = ArmJoints()
        # Fill out joint states
        arm = robot_api.Arm()
        arm.move_to_joints(joints)
    """

    def __init__(self):
        # 创建 actionlib 客户端并等待连接
        self._client = actionlib.SimpleActionClient(ARM_ACTION_NAME, FollowJointTrajectoryAction)
        rospy.loginfo("Waiting for arm action server...")
        self._client.wait_for_server()
        rospy.loginfo("Arm action server connected.")

    def move_to_joints(self, arm_joints):
        """Moves the robot's arm to the given joints."""
        # 创建一个轨迹点
        point = JointTrajectoryPoint()
        point.positions = arm_joints.values()
        point.time_from_start = rospy.Duration(TRAJECTORY_DURATION)

        # 创建轨迹并添加关节名和点
        trajectory = JointTrajectory()
        trajectory.joint_names = ArmJoints.names()
        trajectory.points = [point]

        # 创建目标并设置轨迹
        goal = FollowJointTrajectoryGoal()
        goal.trajectory = trajectory

        # 发送目标并等待结果
        self._client.send_goal(goal)
        self._client.wait_for_result()
        rospy.loginfo("Arm has reached the target position.")


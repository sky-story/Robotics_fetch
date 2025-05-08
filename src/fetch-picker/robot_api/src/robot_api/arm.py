#!/usr/bin/env python3

# TODO: import actionlib
# TODO: import control_msgs.msg
# TODO: import trajectory_msgs.msg
import rospy
import actionlib
from trajectory_msgs.msg import JointTrajectoryPoint, JointTrajectory
from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal

from .arm_joints import ArmJoints

import actionlib
from moveit_msgs.msg import MoveGroupAction, MoveItErrorCodes
from .moveit_goal_builder import MoveItGoalBuilder

# lab20
from moveit_msgs.srv import GetPositionIK, GetPositionIKRequest



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

        # lab19:初始化 trajectory 和 move_group 的 action client
        self._move_group_client = actionlib.SimpleActionClient('move_group', MoveGroupAction)
        rospy.loginfo('Waiting for move_group action server...')
        self._move_group_client.wait_for_server()
        rospy.loginfo('...connected to move_group server!')


        # lab20:初始化 IK 服务
        self._compute_ik = rospy.ServiceProxy('compute_ik', GetPositionIK)

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

    # Lab-19
    # def move_to_pose(self, pose_stamped):
    #     goal_builder = MoveItGoalBuilder()
    #     goal_builder.set_pose_goal(pose_stamped)
    #     goal = goal_builder.build()

    #     self._move_group_client.send_goal(goal)
    #     self._move_group_client.wait_for_result()

    #     result = self._move_group_client.get_result()
    #     if result.error_code.val != MoveItErrorCodes.SUCCESS:
    #         return moveit_error_string(result.error_code.val)
    #     return None
    def move_to_pose(self,
                    pose_stamped,
                    allowed_planning_time=10.0,
                    execution_timeout=15.0,
                    group_name='arm',
                    num_planning_attempts=1,
                    plan_only=False,
                    replan=False,
                    replan_attempts=5,
                    tolerance=0.01,
                    orientation_constraint=None):
        """Moves the end-effector to a pose, using motion planning.

        Args:
            pose_stamped: geometry_msgs/PoseStamped. The goal pose for the gripper.
            allowed_planning_time: float. Max time to wait for planner (sec).
            execution_timeout: float. Max time to wait for execution.
            group_name: string. Joint group to use (arm / arm_with_torso).
            num_planning_attempts: int. Number of times to try planning.
            plan_only: bool. If True, only plan but do not move the arm.
            replan: bool. If True, retry if execution fails.
            replan_attempts: int. Max times to retry on failure.
            tolerance: float. Goal tolerance (in meters).

        Returns:
            None if success; else a string error code.
        """

        goal_builder = MoveItGoalBuilder()
        goal_builder.set_pose_goal(pose_stamped)

        if orientation_constraint is not None:
            goal_builder.add_path_orientation_constraint(orientation_constraint)  

        goal_builder.allowed_planning_time = allowed_planning_time
        goal_builder.num_planning_attempts = num_planning_attempts
        goal_builder.plan_only = plan_only
        goal_builder.replan = replan
        goal_builder.replan_attempts = replan_attempts
        goal_builder.tolerance = tolerance
        goal_builder.group_name = group_name

        goal = goal_builder.build()

        self._move_group_client.send_goal(goal)
        finished = self._move_group_client.wait_for_result(rospy.Duration(execution_timeout))

        if not finished:
            self._move_group_client.cancel_goal()
            return "TIMED_OUT"

        result = self._move_group_client.get_result()
        if result.error_code.val != MoveItErrorCodes.SUCCESS:
            return moveit_error_string(result.error_code.val)

        return None

    
    def cancel_all_goals(self):
        self._client.cancel_all_goals()  # Lab 7 中用的 trajectory controller client
        self._move_group_client.cancel_all_goals()

    def check_pose(self, 
                pose_stamped,
                allowed_planning_time=10.0,
                group_name='arm',
                tolerance=0.01):
        error = self.move_to_pose(
            pose_stamped,
            allowed_planning_time=allowed_planning_time,
            group_name=group_name,
            tolerance=tolerance,
            plan_only=True)
        
        # 如果没有错误，返回 True，表示可达；否则 False
        return error is None


    # lab20
    def compute_ik(self, pose_stamped, timeout=rospy.Duration(5)):
        request = GetPositionIKRequest()
        request.ik_request.pose_stamped = pose_stamped
        request.ik_request.group_name = 'arm'
        request.ik_request.timeout = timeout
        response = self._compute_ik(request)
        error_str = moveit_error_string(response.error_code.val)
        success = error_str == 'SUCCESS'
        if not success:
            return False
        joint_state = response.solution.joint_state
        for name, position in zip(joint_state.name, joint_state.position):
            if name in ArmJoints.names():
                rospy.loginfo('{}: {}'.format(name, position))
        return True

# Lab-19
def moveit_error_string(val):
    """Returns a string associated with a MoveItErrorCode.
        
    Args:
        val: The val field from moveit_msgs/MoveItErrorCodes.msg
        
    Returns: The string associated with the error value, 'UNKNOWN_ERROR_CODE'
        if the value is invalid.
    """ 
    if val == MoveItErrorCodes.SUCCESS:
        return 'SUCCESS'
    elif val == MoveItErrorCodes.FAILURE:
        return 'FAILURE'
    elif val == MoveItErrorCodes.PLANNING_FAILED:
        return 'PLANNING_FAILED'
    elif val == MoveItErrorCodes.INVALID_MOTION_PLAN:
        return 'INVALID_MOTION_PLAN'
    elif val == MoveItErrorCodes.MOTION_PLAN_INVALIDATED_BY_ENVIRONMENT_CHANGE:
        return 'MOTION_PLAN_INVALIDATED_BY_ENVIRONMENT_CHANGE'
    elif val == MoveItErrorCodes.CONTROL_FAILED:
        return 'CONTROL_FAILED'
    elif val == MoveItErrorCodes.UNABLE_TO_AQUIRE_SENSOR_DATA:
        return 'UNABLE_TO_AQUIRE_SENSOR_DATA'
    elif val == MoveItErrorCodes.TIMED_OUT:
        return 'TIMED_OUT'
    elif val == MoveItErrorCodes.PREEMPTED:
        return 'PREEMPTED'
    elif val == MoveItErrorCodes.START_STATE_IN_COLLISION:
        return 'START_STATE_IN_COLLISION'
    elif val == MoveItErrorCodes.START_STATE_VIOLATES_PATH_CONSTRAINTS:
        return 'START_STATE_VIOLATES_PATH_CONSTRAINTS'
    elif val == MoveItErrorCodes.GOAL_IN_COLLISION:
        return 'GOAL_IN_COLLISION'
    elif val == MoveItErrorCodes.GOAL_VIOLATES_PATH_CONSTRAINTS:
        return 'GOAL_VIOLATES_PATH_CONSTRAINTS'
    elif val == MoveItErrorCodes.GOAL_CONSTRAINTS_VIOLATED:
        return 'GOAL_CONSTRAINTS_VIOLATED'
    elif val == MoveItErrorCodes.INVALID_GROUP_NAME:
        return 'INVALID_GROUP_NAME'
    elif val == MoveItErrorCodes.INVALID_GOAL_CONSTRAINTS:
        return 'INVALID_GOAL_CONSTRAINTS'
    elif val == MoveItErrorCodes.INVALID_ROBOT_STATE:
        return 'INVALID_ROBOT_STATE'
    elif val == MoveItErrorCodes.INVALID_LINK_NAME:
        return 'INVALID_LINK_NAME'                                      
    elif val == MoveItErrorCodes.INVALID_OBJECT_NAME:
        return 'INVALID_OBJECT_NAME'
    elif val == MoveItErrorCodes.FRAME_TRANSFORM_FAILURE:
        return 'FRAME_TRANSFORM_FAILURE'
    elif val == MoveItErrorCodes.COLLISION_CHECKING_UNAVAILABLE:
        return 'COLLISION_CHECKING_UNAVAILABLE'
    elif val == MoveItErrorCodes.ROBOT_STATE_STALE:
        return 'ROBOT_STATE_STALE'
    elif val == MoveItErrorCodes.SENSOR_INFO_STALE:
        return 'SENSOR_INFO_STALE'
    elif val == MoveItErrorCodes.NO_IK_SOLUTION:
        return 'NO_IK_SOLUTION'
    else:
        return 'UNKNOWN_ERROR_CODE'




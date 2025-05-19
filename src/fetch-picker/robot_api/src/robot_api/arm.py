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

    def __init__(self):
        # 初始化轨迹控制器客户端
        self._client = actionlib.SimpleActionClient(ARM_ACTION_NAME, FollowJointTrajectoryAction)
        rospy.loginfo("等待机械臂action服务器...")
        self._client.wait_for_server()
        rospy.loginfo("机械臂action服务器已连接")

        # lab19:初始化 trajectory 和 move_group 的 action client
        self._move_group_client = actionlib.SimpleActionClient('move_group', MoveGroupAction)
        rospy.loginfo('等待move_group action服务器...')
        self._move_group_client.wait_for_server()
        rospy.loginfo('已连接到move_group服务器!')


        # lab20:初始化 IK 服务
        self._compute_ik = rospy.ServiceProxy('compute_ik', GetPositionIK)

    def move_to_joints(self, arm_joints):
        """控制机械臂移动到指定的关节角度
        
        Args:
            arm_joints: ArmJoints对象，包含目标关节角度
        """
        # 创建轨迹点
        point = JointTrajectoryPoint()
        point.positions = arm_joints.values()
        point.time_from_start = rospy.Duration(TRAJECTORY_DURATION)

        # 创建轨迹消息
        trajectory = JointTrajectory()
        trajectory.joint_names = ArmJoints.names()
        trajectory.points = [point]

        # 创建并发送目标
        goal = FollowJointTrajectoryGoal()
        goal.trajectory = trajectory
        self._client.send_goal(goal)
        self._client.wait_for_result()
        rospy.loginfo("机械臂已到达目标位置")

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
        # 创建规划目标
        goal_builder = MoveItGoalBuilder()
        goal_builder.set_pose_goal(pose_stamped)

        # 添加姿态约束（如果有）
        if orientation_constraint is not None:
            goal_builder.add_path_orientation_constraint(orientation_constraint)  

        # 设置规划参数
        goal_builder.allowed_planning_time = allowed_planning_time
        goal_builder.num_planning_attempts = num_planning_attempts
        goal_builder.plan_only = plan_only
        goal_builder.replan = replan
        goal_builder.replan_attempts = replan_attempts
        goal_builder.tolerance = tolerance
        goal_builder.group_name = group_name

        # 构建并发送目标
        goal = goal_builder.build()
        self._move_group_client.send_goal(goal)
        finished = self._move_group_client.wait_for_result(rospy.Duration(execution_timeout))

        # 处理执行结果
        if not finished:
            self._move_group_client.cancel_goal()
            return "TIMED_OUT"

        result = self._move_group_client.get_result()
        if result.error_code.val != MoveItErrorCodes.SUCCESS:
            return moveit_error_string(result.error_code.val)

        return None

    
    def cancel_all_goals(self):
        self._client.cancel_all_goals()  
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
        
        return error is None


    # lab20
    def compute_ik(self, pose_stamped, timeout=rospy.Duration(5)):

        request = GetPositionIKRequest()
        request.ik_request.pose_stamped = pose_stamped
        request.ik_request.group_name = 'arm'
        request.ik_request.timeout = timeout
        response = self._compute_ik(request)
        
        # 检查计算结果
        error_str = moveit_error_string(response.error_code.val)
        success = error_str == 'SUCCESS'
        if not success:
            return False
            
        # 输出关节角度
        joint_state = response.solution.joint_state
        for name, position in zip(joint_state.name, joint_state.position):
            if name in ArmJoints.names():
                rospy.loginfo('{}: {}'.format(name, position))
        return True

# Lab-19
def moveit_error_string(val):
    # 错误代码映射表
    error_codes = {
        MoveItErrorCodes.SUCCESS: 'SUCCESS',
        MoveItErrorCodes.FAILURE: 'FAILURE',
        MoveItErrorCodes.PLANNING_FAILED: 'PLANNING_FAILED',
        MoveItErrorCodes.INVALID_MOTION_PLAN: 'INVALID_MOTION_PLAN',
        MoveItErrorCodes.MOTION_PLAN_INVALIDATED_BY_ENVIRONMENT_CHANGE: 'MOTION_PLAN_INVALIDATED_BY_ENVIRONMENT_CHANGE',
        MoveItErrorCodes.CONTROL_FAILED: 'CONTROL_FAILED',
        MoveItErrorCodes.UNABLE_TO_AQUIRE_SENSOR_DATA: 'UNABLE_TO_AQUIRE_SENSOR_DATA',
        MoveItErrorCodes.TIMED_OUT: 'TIMED_OUT',
        MoveItErrorCodes.PREEMPTED: 'PREEMPTED',
        MoveItErrorCodes.START_STATE_IN_COLLISION: 'START_STATE_IN_COLLISION',
        MoveItErrorCodes.START_STATE_VIOLATES_PATH_CONSTRAINTS: 'START_STATE_VIOLATES_PATH_CONSTRAINTS',
        MoveItErrorCodes.GOAL_IN_COLLISION: 'GOAL_IN_COLLISION',
        MoveItErrorCodes.GOAL_VIOLATES_PATH_CONSTRAINTS: 'GOAL_VIOLATES_PATH_CONSTRAINTS',
        MoveItErrorCodes.GOAL_CONSTRAINTS_VIOLATED: 'GOAL_CONSTRAINTS_VIOLATED',
        MoveItErrorCodes.INVALID_GROUP_NAME: 'INVALID_GROUP_NAME',
        MoveItErrorCodes.INVALID_GOAL_CONSTRAINTS: 'INVALID_GOAL_CONSTRAINTS',
        MoveItErrorCodes.INVALID_ROBOT_STATE: 'INVALID_ROBOT_STATE',
        MoveItErrorCodes.INVALID_LINK_NAME: 'INVALID_LINK_NAME',
        MoveItErrorCodes.INVALID_OBJECT_NAME: 'INVALID_OBJECT_NAME',
        MoveItErrorCodes.FRAME_TRANSFORM_FAILURE: 'FRAME_TRANSFORM_FAILURE',
        MoveItErrorCodes.COLLISION_CHECKING_UNAVAILABLE: 'COLLISION_CHECKING_UNAVAILABLE',
        MoveItErrorCodes.ROBOT_STATE_STALE: 'ROBOT_STATE_STALE',
        MoveItErrorCodes.SENSOR_INFO_STALE: 'SENSOR_INFO_STALE',
        MoveItErrorCodes.NO_IK_SOLUTION: 'NO_IK_SOLUTION'
    }
    
    return error_codes.get(val, 'UNKNOWN_ERROR_CODE')




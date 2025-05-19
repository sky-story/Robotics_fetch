#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped  
from moveit_msgs.msg import OrientationConstraint  
from moveit_python import PlanningSceneInterface  #
import robot_api  

def main():
    """
    主函数：演示机械臂在有障碍物环境中的运动规划
    包括：
    1. 添加桌面障碍物
    2. 模拟抓取托盘
    3. 执行两个目标位置的移动
    """

    rospy.init_node('arm_obstacle_demo')

    planning_scene = PlanningSceneInterface('base_link')

    # 清除场景中可能存在的旧障碍物
    planning_scene.removeCollisionObject('table')
    planning_scene.removeCollisionObject('divider')
    planning_scene.removeAttachedObject('tray')  

    rospy.sleep(1) 

    # 添加桌面障碍物
    table_size_x, table_size_y, table_size_z = 0.5, 1.0, 0.03 
    table_x, table_y, table_z = 0.8, 0.0, 0.6  
    planning_scene.addBox('table', table_size_x, table_size_y, table_size_z,
                          table_x, table_y, table_z)

    # 模拟抓取托盘，将其附加到夹爪上
    planning_scene.attachBox(
        'tray', 0.3, 0.07, 0.01,  
        0.05, 0, 0,  # 托盘相对于夹爪的位置偏移
        'gripper_link',  # 附着到夹爪连杆
        ['gripper_link', 'l_gripper_finger_link', 'r_gripper_finger_link']  # 允许碰撞的连杆列表
    )
    planning_scene.setColor('tray', 1, 0, 1) 
    planning_scene.sendColors() 

    rospy.sleep(1)  
    
    arm = robot_api.Arm()

    def shutdown():
        """确保在程序退出时取消所有正在执行的目标"""
        arm.cancel_all_goals()
    rospy.on_shutdown(shutdown)

    # 设置第一个目标位置（divider左侧）
    pose1 = PoseStamped()
    pose1.header.frame_id = 'base_link'
    pose1.pose.position.x = 0.5
    pose1.pose.position.y = -0.3
    pose1.pose.position.z = 0.75
    pose1.pose.orientation.w = 1

    # 设置第二个目标位置（divider右侧）
    pose2 = PoseStamped()
    pose2.header.frame_id = 'base_link'
    pose2.pose.position.x = 0.5
    pose2.pose.position.y = 0.3
    pose2.pose.position.z = 0.75
    pose2.pose.orientation.w = 1

    # 创建姿态约束：保持末端执行器朝上（不倾斜）
    oc = OrientationConstraint()
    oc.header.frame_id = 'base_link'
    oc.link_name = 'wrist_roll_link'  # 约束应用在手腕连杆上
    oc.orientation.w = 1  # 保持默认姿态（不旋转）
    oc.absolute_x_axis_tolerance = 0.1  # X轴允许的偏差
    oc.absolute_y_axis_tolerance = 0.1  # Y轴允许的偏差
    oc.absolute_z_axis_tolerance = 3.14  # Z轴允许的偏差（较大，允许绕Z轴旋转）
    oc.weight = 1.0  # 约束权重

    kwargs = {
        'allowed_planning_time': 15, 
        'execution_timeout': 10, 
        'num_planning_attempts': 5,  
        'replan': False  
    }

    # 移动到第一个位置（不使用姿态约束）
    error = arm.move_to_pose(pose1, **kwargs)
    if error is not None:
        rospy.logerr('Pose 1 failed: {}'.format(error))
        return
    else:
        rospy.loginfo('Pose 1 succeeded')

    rospy.sleep(1) 

    # 移动到第二个位置（使用姿态约束保持托盘水平）
    error = arm.move_to_pose(pose2, orientation_constraint=oc, **kwargs)
    if error is not None:
        rospy.logerr('Pose 2 failed: {}'.format(error))
    else:
        rospy.loginfo('Pose 2 succeeded')
        
    planning_scene.removeCollisionObject('table')
    planning_scene.removeAttachedObject('tray')

if __name__ == '__main__':
    main()

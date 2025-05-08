#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from moveit_msgs.msg import OrientationConstraint
from moveit_python import PlanningSceneInterface
import robot_api

def main():
    rospy.init_node('arm_obstacle_demo')
    planning_scene = PlanningSceneInterface('base_link')

    # 清除旧障碍物
    planning_scene.removeCollisionObject('table')
    planning_scene.removeCollisionObject('divider')
    planning_scene.removeAttachedObject('tray')  # 防止有残留附着物

    rospy.sleep(1)  # 给系统时间处理删除

    # 添加桌子
    table_size_x, table_size_y, table_size_z = 0.5, 1.0, 0.03
    table_x, table_y, table_z = 0.8, 0.0, 0.6
    planning_scene.addBox('table', table_size_x, table_size_y, table_size_z,
                          table_x, table_y, table_z)

    # 模拟抓取一个物体（托盘），附加到夹爪
    planning_scene.attachBox(
        'tray', 0.3, 0.07, 0.01,  # 长宽高
        0.05, 0, 0,  # 相对夹爪的位置
        'gripper_link',
        ['gripper_link', 'l_gripper_finger_link', 'r_gripper_finger_link']
    )
    planning_scene.setColor('tray', 1, 0, 1)  # 紫色托盘
    planning_scene.sendColors()

    rospy.sleep(1)  # 等待场景更新

    arm = robot_api.Arm()

    def shutdown():
        arm.cancel_all_goals()
    rospy.on_shutdown(shutdown)

    # 第一个目标姿态（divider 左侧）
    pose1 = PoseStamped()
    pose1.header.frame_id = 'base_link'
    pose1.pose.position.x = 0.5
    pose1.pose.position.y = -0.3
    pose1.pose.position.z = 0.75
    pose1.pose.orientation.w = 1

    # 第二个目标姿态（divider 右侧）
    pose2 = PoseStamped()
    pose2.header.frame_id = 'base_link'
    pose2.pose.position.x = 0.5
    pose2.pose.position.y = 0.3
    pose2.pose.position.z = 0.75
    pose2.pose.orientation.w = 1

    # 添加方向约束：保持末端执行器朝上（不倾斜）
    oc = OrientationConstraint()
    oc.header.frame_id = 'base_link'
    oc.link_name = 'wrist_roll_link'
    oc.orientation.w = 1  # 不旋转
    oc.absolute_x_axis_tolerance = 0.1
    oc.absolute_y_axis_tolerance = 0.1
    oc.absolute_z_axis_tolerance = 3.14
    oc.weight = 1.0

    # 公共路径规划参数
    kwargs = {
        'allowed_planning_time': 15,
        'execution_timeout': 10,
        'num_planning_attempts': 5,
        'replan': False
    }

    # 移动到 pose1，不加方向约束
    error = arm.move_to_pose(pose1, **kwargs)
    if error is not None:
        rospy.logerr('Pose 1 failed: {}'.format(error))
        return
    else:
        rospy.loginfo('Pose 1 succeeded')

    rospy.sleep(1)

    # 移动到 pose2，加上方向约束（保持托盘水平）
    error = arm.move_to_pose(pose2, orientation_constraint=oc, **kwargs)
    if error is not None:
        rospy.logerr('Pose 2 failed: {}'.format(error))
    else:
        rospy.loginfo('Pose 2 succeeded')

    # 清除障碍物和附着物
    planning_scene.removeCollisionObject('table')
    planning_scene.removeAttachedObject('tray')

if __name__ == '__main__':
    main()

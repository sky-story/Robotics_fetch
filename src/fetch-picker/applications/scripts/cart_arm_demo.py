#!/usr/bin/env python

# 导入必要的ROS和机器人API库
import rospy
from geometry_msgs.msg import Pose, Point, Quaternion, PoseStamped
from robot_api.arm import Arm

def main():
    rospy.init_node('cart_arm_demo')
    arm = Arm()

    def shutdown():
        """
        确保在程序退出时取消所有正在执行的目标
        """
        arm.cancel_all_goals()
    rospy.on_shutdown(shutdown)

    pose1 = Pose(
        Point(0.042, 0.384, 1.826),  
        Quaternion(0.173, -0.693, -0.242, 0.657) 
    )

    pose2 = Pose(
        Point(0.047, 0.545, 1.822), 
        Quaternion(-0.274, -0.701, 0.173, 0.635)  
    )

    # 创建PoseStamped消息，添加坐标系信息
    ps1 = PoseStamped()
    ps1.header.frame_id = 'base_link'  # 相对于机器人基座坐标系
    ps1.pose = pose1

    ps2 = PoseStamped()
    ps2.header.frame_id = 'base_link'  # 相对于机器人基座坐标系
    ps2.pose = pose2

    gripper_poses = [ps1, ps2]


    rate = rospy.Rate(0.5)
    
    # 主循环
    while not rospy.is_shutdown():
        # 依次访问每个位姿
        for pose in gripper_poses:
            # 控制机械臂移动到目标位姿
            error = arm.move_to_pose(pose)
            # 如果发生错误，记录错误信息
            if error is not None:
                rospy.logerr(error)
            rospy.sleep(1)
            # 按照设定的频率休眠
            rate.sleep()

if __name__ == '__main__':
    main()

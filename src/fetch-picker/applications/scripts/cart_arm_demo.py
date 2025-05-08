#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Pose, Point, Quaternion, PoseStamped
from robot_api.arm import Arm

def main():
    rospy.init_node('cart_arm_demo')
    arm = Arm()

    def shutdown():
        arm.cancel_all_goals()
    rospy.on_shutdown(shutdown)

    pose1 = Pose(Point(0.042, 0.384, 1.826), Quaternion(0.173, -0.693, -0.242, 0.657))
    pose2 = Pose(Point(0.047, 0.545, 1.822), Quaternion(-0.274, -0.701, 0.173, 0.635))

    ps1 = PoseStamped()
    ps1.header.frame_id = 'base_link'
    ps1.pose = pose1

    ps2 = PoseStamped()
    ps2.header.frame_id = 'base_link'
    ps2.pose = pose2

    gripper_poses = [ps1, ps2]

    rate = rospy.Rate(0.5)
    while not rospy.is_shutdown():
        for pose in gripper_poses:
            error = arm.move_to_pose(pose)
            if error is not None:
                rospy.logerr(error)
            rospy.sleep(1)
            rate.sleep()

if __name__ == '__main__':
    main()

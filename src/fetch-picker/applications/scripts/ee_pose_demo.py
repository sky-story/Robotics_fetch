#!/usr/bin/env python
import rospy
import tf

def main():
    rospy.init_node('ee_pose_demo')
    listener = tf.TransformListener()

    rospy.sleep(0.2)  # 给 TF 一点时间接收消息

    rate = rospy.Rate(1.0)  # 1 Hz
    while not rospy.is_shutdown():
        try:
            # 读取 gripper_link 相对 base_link 的位置和朝向
            (trans, rot) = listener.lookupTransform("base_link", "gripper_link", rospy.Time(0))
            rospy.loginfo("position: {}".format(trans))
            rospy.loginfo("orientation: {}".format(rot))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as e:
            rospy.logwarn(str(e))

        rate.sleep()

if __name__ == '__main__':
    main()

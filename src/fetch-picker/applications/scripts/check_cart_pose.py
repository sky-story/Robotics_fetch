#!/usr/bin/env python

from geometry_msgs.msg import PoseStamped 
import robot_api  
import rospy  

def wait_for_time():
    while rospy.Time().now().to_sec() == 0:
        pass

def print_usage():

    print('Usage: rosrun applications check_cart_pose.py plan X Y Z')
    print('       rosrun applications check_cart_pose.py ik X Y Z')

def main():

    rospy.init_node('check_cart_pose')
    wait_for_time()
    
    argv = rospy.myargv()
    if len(argv) < 5:
        print_usage()
        return
    
    # 解析命令行参数
    command, x, y, z = argv[1], float(argv[2]), float(argv[3]), float(argv[4])

    # 创建机械臂控制对象
    arm = robot_api.Arm()
    
    # 创建位姿消息
    ps = PoseStamped()
    ps.header.frame_id = 'base_link'  
    ps.pose.position.x = x  
    ps.pose.position.y = y  
    ps.pose.position.z = z  
    ps.pose.orientation.w = 1 

    # 根据命令执行不同的操作
    if command == 'plan':
        # 检查位姿是否可达（运动规划）
        error = arm.check_pose(ps, allowed_planning_time=1.0)
        if error is None:
            rospy.loginfo('Found plan!')  
        else:
            rospy.loginfo('No plan found.')  
        arm.cancel_all_goals()  
    elif command == 'ik':
        # 检查逆运动学解是否存在
        if arm.compute_ik(ps):
            rospy.loginfo('Found IK!')  
        else:
            rospy.loginfo('No IK found.')  
    else:
        print_usage()  # 如果命令无效，显示使用说明

if __name__ == '__main__':
    main()


#!/usr/bin/env python3

# 导入必要的ROS和MoveIt相关库
import rospy
from moveit_python import PlanningSceneInterface  
from moveit_msgs.msg import PlanningScene, ObjectColor  
from std_msgs.msg import ColorRGBA 

def wait_for_time():
    while rospy.Time().now().to_sec() == 0:
        pass

def main():
    """
    主函数：创建和管理规划场景中的障碍物
    包括：
    1. 添加地板和桌子作为障碍物
    2. 设置障碍物的颜色
    3. 发布规划场景信息
    """
    # 初始化ROS节点
    rospy.init_node('lab26_obstacles')

    # 等待ROS时间系统初始化
    wait_for_time()

    # 所有障碍物的位置都相对于机器人基座坐标系（base_link）
    planning_scene = PlanningSceneInterface('base_link')

    # 清理场景：移除可能存在的旧障碍物
    planning_scene.clear()  # 清除所有障碍物
    planning_scene.removeCollisionObject('table')  # 移除桌子
    planning_scene.removeCollisionObject('floor')  # 移除地板


    planning_scene.addBox('floor', 2.0, 2.0, 0.01, 0.0, 0.0, 0.005)
    planning_scene.addBox('table', 0.5, 1.0, 0.72, 1.0, 0.0, 0.72 / 2)

    rospy.sleep(2)

    scene_pub = rospy.Publisher('/planning_scene', PlanningScene, queue_size=10)

    rospy.sleep(1)

    grey = ColorRGBA()
    grey.r = 0.5  
    grey.g = 0.5  
    grey.b = 0.5  
    grey.a = 1.0  


    floor_color = ObjectColor()
    floor_color.id = 'floor'  
    floor_color.color = grey   

    table_color = ObjectColor()
    table_color.id = 'table'   
    table_color.color = grey  

    planning_scene_msg = PlanningScene()
    planning_scene_msg.is_diff = True  
    # 添加颜色信息
    planning_scene_msg.object_colors.append(floor_color)
    planning_scene_msg.object_colors.append(table_color)

    # 发布规划场景消息
    scene_pub.publish(planning_scene_msg)

    rospy.sleep(1)

if __name__ == '__main__':
    main()

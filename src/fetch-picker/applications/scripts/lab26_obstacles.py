#!/usr/bin/env python3

import rospy
from moveit_python import PlanningSceneInterface
from moveit_msgs.msg import PlanningScene, ObjectColor
from std_msgs.msg import ColorRGBA

def wait_for_time():
    """等待仿真时间启动"""
    while rospy.Time().now().to_sec() == 0:
        pass

def main():
    # 初始化 ROS 节点
    rospy.init_node('lab26_obstacles')

    # 等待仿真时间启动
    wait_for_time()

    # 创建规划场景接口（参考系设置为 base_link）
    planning_scene = PlanningSceneInterface('base_link')

    # 清空已有的物体信息（以防上一次运行遗留）
    planning_scene.clear()
    planning_scene.removeCollisionObject('table')
    planning_scene.removeCollisionObject('floor')

    # 添加地板：2m x 2m，厚度0.01m，放在 z = 0.005m（即0.01的一半）
    planning_scene.addBox('floor', 2.0, 2.0, 0.01, 0.0, 0.0, 0.005)

    # 添加桌子：0.5m x 1.0m，高度 0.72m，中心点 z = 0.72 / 2
    planning_scene.addBox('table', 0.5, 1.0, 0.72, 1.0, 0.0, 0.72 / 2)

    # 等待几秒确保物体被加入场景中
    rospy.sleep(2)

    # 创建一个用于发布颜色的 Publisher
    scene_pub = rospy.Publisher('/planning_scene', PlanningScene, queue_size=10)

    # 等待 Publisher 初始化完成
    rospy.sleep(1)

    # 定义灰色（RGBA）
    grey = ColorRGBA()
    grey.r = 0.5
    grey.g = 0.5
    grey.b = 0.5
    grey.a = 1.0  # 不透明

    # 给地板添加颜色
    floor_color = ObjectColor()
    floor_color.id = 'floor'
    floor_color.color = grey

    # 给桌子添加颜色
    table_color = ObjectColor()
    table_color.id = 'table'
    table_color.color = grey

    # 创建并发布 PlanningScene 消息，附加颜色信息
    planning_scene_msg = PlanningScene()
    planning_scene_msg.is_diff = True  # 只发布差异
    planning_scene_msg.object_colors.append(floor_color)
    planning_scene_msg.object_colors.append(table_color)

    scene_pub.publish(planning_scene_msg)

    # 再等一会，确保发布完成
    rospy.sleep(1)

if __name__ == '__main__':
    main()

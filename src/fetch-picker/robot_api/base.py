import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import copy
import math
from tf.transformations import euler_from_quaternion

class Base(object):
    def __init__(self):
        self._cmd_pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self._odom_sub = rospy.Subscriber('odom', Odometry, self._odom_callback)
        self._latest_odom = None

    def _odom_callback(self, msg):
        self._latest_odom = msg

    def move(self, linear, angular):
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        self._cmd_pub.publish(twist)

    def _get_current_position(self):
        return self._latest_odom.pose.pose.position

    def _get_current_yaw(self):
        ori = self._latest_odom.pose.pose.orientation
        _, _, yaw = euler_from_quaternion([ori.x, ori.y, ori.z, ori.w])
        return yaw
    
    def go_forward(self, distance, speed=0.1):
        while self._latest_odom is None:
            rospy.sleep(0.1)

        start = copy.deepcopy(self._latest_odom.pose.pose.position)
        rate = rospy.Rate(10)
        direction = -1 if distance < 0 else 1
        distance = abs(distance)

        def dist_moved(current, start):
            dx = current.x - start.x
            dy = current.y - start.y
            return math.sqrt(dx*dx + dy*dy)

        while dist_moved(self._get_current_position(), start) < distance:
            remaining = distance - dist_moved(self._get_current_position(), start)
            linear_speed = max(0.05, min(0.5, remaining))
            self.move(direction * linear_speed, 0)
            rate.sleep()

        self.move(0, 0)  # 停止
        
    def turn(self, angular_distance, speed=0.5):
        while self._latest_odom is None:
            rospy.sleep(0.1)

        start_yaw = self._get_current_yaw()
        rate = rospy.Rate(10)
        direction = -1 if angular_distance < 0 else 1
        remaining = abs(angular_distance) % (2 * math.pi)

        def normalize(yaw):
            return yaw % (2 * math.pi)

        while True:
            current_yaw = normalize(self._get_current_yaw())
            start_norm = normalize(start_yaw)
            delta = normalize(current_yaw - start_norm)
            rotated = delta if direction == 1 else normalize(start_norm - current_yaw)
            if rotated >= remaining:
                break

            speed_scaled = max(0.25, min(1.0, remaining - rotated))
            self.move(0, direction * speed_scaled)
            rate.sleep()

        self.move(0, 0)



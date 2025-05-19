import rosbag
import rospy
from sensor_msgs.msg import PointCloud2


class MockCamera(object):
    def __init__(self):
        pass

    def read_cloud(self, path):
        try:
            with rosbag.Bag(path, 'r') as bag:
                print(f"Opened bag file: {path}")
                for topic, msg, t in bag.read_messages():
                    msg_type = msg._type if hasattr(msg, '_type') else type(msg)
                    print(f"Read topic: {topic}, type: {msg_type}")
                    if getattr(msg, '_type', '') == 'sensor_msgs/PointCloud2':
                        print("Found PointCloud2 message.")
                        return msg
                print("No PointCloud2 message found in bag.")
        except Exception as e:
            print(f"Error reading bag file: {e}")
        return None


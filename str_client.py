import rospy
import json
from string_service_demo.srv import StringService

def main():
    rospy.init_node('string_service_client')
    rospy.wait_for_service('/send_string')
    proxy = rospy.ServiceProxy('/send_string', StringService)

    with open('/fetch_ws/test_data.json', 'r') as f:
        json_data = json.load(f)

    json_string = json.dumps(json_data)

    response = proxy(json_string)
    rospy.loginfo("Response from server: %s", response.result)

if __name__ == "__main__":
    main()

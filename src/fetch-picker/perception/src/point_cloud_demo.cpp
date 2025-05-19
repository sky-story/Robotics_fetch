#include "perception/crop.h"
#include "perception/downsample.h"
#include "ros/ros.h"
#include "sensor_msgs/PointCloud2.h"

int main(int argc, char** argv) {
    ros::init(argc, argv, "point_cloud_demo");
    ros::NodeHandle nh;

    // 裁剪后发布 cropped_cloud
    ros::Publisher crop_pub =
        nh.advertise<sensor_msgs::PointCloud2>("cropped_cloud", 1, true);
    perception::Cropper cropper(crop_pub);
    ros::Subscriber sub =
        nh.subscribe("cloud_in", 1, &perception::Cropper::Callback, &cropper);

    // 下采样裁剪结果，再发布 downsampled_cloud
    ros::Publisher downsample_pub =
        nh.advertise<sensor_msgs::PointCloud2>("downsampled_cloud", 1, true);
    perception::Downsampler downsampler(downsample_pub);
    ros::Subscriber sub2 =
        nh.subscribe("cropped_cloud", 1, &perception::Downsampler::Callback, &downsampler);

    ros::spin();
    return 0;
}

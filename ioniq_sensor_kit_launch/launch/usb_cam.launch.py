from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import PathJoinSubstitution
import os


def generate_launch_description():
    # Launch arguments
    node_name = LaunchConfiguration('node_name')
    params_file = LaunchConfiguration('params_file')
    
    kit_dir = get_package_share_directory('ioniq_sensor_kit_launch')
    default_params_path = os.path.join(kit_dir, 'config', 'camera0.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('node_name', default_value='usb_cam'),
        DeclareLaunchArgument('params_file', default_value=default_params_path),

        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            name=node_name,
            output='screen',
            parameters=[params_file],
            remappings=[
                ('image_raw', PathJoinSubstitution(['/sensing/camera', node_name, 'image_rect_color'])),
                # ('image_raw/compressed', PathJoinSubstitution(['/sensing/camera', node_name, 'image_rect_color'])),
                ('image_raw/compressedDepth', PathJoinSubstitution(['/sensing/camera', node_name, 'image_raw/compressedDepth'])),
                ('image_raw/theora', PathJoinSubstitution(['/sensing/camera', node_name, 'image_raw/theora'])),
                ('camera_info', PathJoinSubstitution(['/sensing/camera', node_name, 'camera_info'])),
            ]
        )
        #,

        # Node(
        #     package='image_proc',
        #     executable='image_proc',
        #     name='rectify_camera_image_node',
        #     output='screen',
        #     remappings=[
        #         ('image', PathJoinSubstitution(['/sensing/camera', node_name, 'image_raw'])),
        #         ('camera_info', PathJoinSubstitution(['/sensing/camera', node_name, 'camera_info'])),
        #         ('image_rect', PathJoinSubstitution(['/sensing/camera', node_name, 'image_rect_color']))
        #     ]
        # )
    ])

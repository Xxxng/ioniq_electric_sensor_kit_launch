from launch import LaunchDescription
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

def generate_launch_description():
    return LaunchDescription([
        ComposableNodeContainer(
            name='camera_node_container',
            namespace='',
            package='rclcpp_components',
            executable='component_container_mt',
            composable_node_descriptions=[
                ComposableNode(
                    package='usb_cam',
                    plugin='usb_cam::UsbCamNode',
                    name='usb_cam_node',
                    parameters=[{
                        'camera_name': 'camera0',
                        'video_device': '/dev/video0',
                        'image_width': 640,
                        'image_height': 480,
                        'pixel_format': 'yuyv',  # or 'mjpeg'
                        'io_method': 'mmap',
                        'framerate': 30.0,
                        'frame_id': 'camera0_link',
                        'autoexposure': True,
                        'autofocus': False,
                        'auto_white_balance': True,
                        'brightness': -1,
                        'contrast': -1,
                        'saturation': -1,
                        'sharpness': -1,
                        'gain': -1,
                        'exposure': 100,
                        'focus': -1,
                    }]
                ),
            ],
            output='screen'
        )
    ])

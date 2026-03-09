# # Copyright 2020 Tier IV, Inc. All rights reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #     http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.

import launch
from launch.actions import DeclareLaunchArgument
from launch.actions import SetLaunchConfiguration
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.substitutions import FindPackageShare
from launch.actions import OpaqueFunction
import yaml

def launch_setup(context, *args, **kwargs):
    camera_container_name = LaunchConfiguration("camera_container_name").perform(context)
    output_topic= LaunchConfiguration("output_topic").perform(context)
    image_name = LaunchConfiguration("input_image").perform(context)
    gpu_id = int(LaunchConfiguration("gpu_id").perform(context))
    mode = LaunchConfiguration("mode").perform(context)
    calib_image_directory = FindPackageShare("autoware_tensorrt_yolox").perform(context) + "/calib_image/"
    tensorrt_config_path = FindPackageShare('autoware_tensorrt_yolox').perform(context)+ "/config/" + LaunchConfiguration("yolo_type").perform(context) + ".param.yaml"

    with open(tensorrt_config_path, "r") as f:
        tensorrt_yaml_param = yaml.safe_load(f)["/**"]["ros__parameters"]

    camera_model_param_path = LaunchConfiguration("camera_model_param_path").perform(context)
    # with open(camera_model_param_path, "r") as f:
    #     camera_model_yaml_param = yaml.safe_load(f)["/**"]["ros__parameters"]
    # camera_param_path=FindPackageShare("lucid_vision_driver").perform(context)+"/param/"+image_name+".param.yaml"
    # with open(camera_param_path, "r") as f:
    #     camera_yaml_param = yaml.safe_load(f)["/**"]["ros__parameters"]

    with open(camera_model_param_path, "r") as f:
        camera_model_yaml_param = yaml.safe_load(f)

# 전체 ros__parameters 그대로 전달
    camera_parameters = camera_model_yaml_param["/**"]["ros__parameters"]

    # rotate.config 파일 읽기
    rotate_config_path = LaunchConfiguration("rorate_config_path").perform(context)
    with open(rotate_config_path, "r") as f:
        rotate_yaml_param = yaml.safe_load(f)

    # rotate.config의 파라미터를 적용
    rotate_parameters = rotate_yaml_param["/**"]["ros__parameters"]

    container = ComposableNodeContainer(
        name=camera_container_name,
        namespace="",
        package="rclcpp_components",
        executable=LaunchConfiguration("container_executable"),
        output="screen",
        composable_node_descriptions=[
            ComposableNode(
                package='usb_cam',
                plugin='usb_cam::UsbCamNode',
                name='usb_cam_node',
                parameters=[camera_parameters],
                remappings=[('camera_info', '/sensing/camera/camera0/camera_info')]
            ),
            ComposableNode(
                package='image_rotate',
                plugin='image_rotate::ImageRotateNode',
                name='image_rotate_node',
                parameters=[rotate_parameters],
                remappings=[('image', '/image_raw'),
                        ('camera_info', '/sensing/camera/camera0/camera_info'),
                        ('rotated/image', '/sensing/camera/camera0/image_rect_color')]
            )
            # ,

            # ComposableNode(
            #     namespace='/perception/object_recognition/detection',
            #     package="autoware_tensorrt_yolox",
            #     plugin="object_recognition::TensorrtYoloNodelet",
            #     name="autoware_tensorrt_yolox",
            #     parameters=[
            #         {
            #             "mode": mode,
            #             "gpu_id": gpu_id,
            #             "onnx_file": FindPackageShare("autoware_tensorrt_yolox").perform(context) +  "/data/" + LaunchConfiguration("yolo_type").perform(context) + ".onnx",
            #             "label_file": FindPackageShare("autoware_tensorrt_yolox").perform(context) + "/data/" + LaunchConfiguration("label_file").perform(context),
            #             "engine_file": FindPackageShare("autoware_tensorrt_yolox").perform(context) + "/data/"+ LaunchConfiguration("yolo_type").perform(context) + ".engine",
            #             "calib_image_directory": calib_image_directory,
            #             "calib_cache_file": FindPackageShare("autoware_tensorrt_yolox").perform(context) + "/data/" + LaunchConfiguration("yolo_type").perform(context) + ".cache",
            #             "num_anchors": tensorrt_yaml_param['num_anchors'],
            #             "anchors": tensorrt_yaml_param['anchors'],
            #             "scale_x_y": tensorrt_yaml_param['scale_x_y'],
            #             "score_threshold": tensorrt_yaml_param['score_threshold'],
            #             "iou_thresh": tensorrt_yaml_param['iou_thresh'],
            #             "detections_per_im": tensorrt_yaml_param['detections_per_im'],
            #             "use_darknet_layer": tensorrt_yaml_param['use_darknet_layer'],
            #             "ignore_thresh": tensorrt_yaml_param['ignore_thresh'],
            #         }
            #     ],
            #     remappings=[
            #         ("in/image", image_name),
            #         ("out/objects", output_topic),
            #         ("out/image", output_topic + "/debug/image"),
            #     ],
            #     extra_arguments=[
            #         {"use_intra_process_comms": LaunchConfiguration("use_intra_process")}
            #     ],
            # ),
        ]

    )
    return [container]


def generate_launch_description():
    launch_arguments = []

    def add_launch_arg(name: str, default_value=None, description=None):
        # a default_value of None is equivalent to not passing that kwarg at all
        launch_arguments.append(
            DeclareLaunchArgument(name, default_value=default_value, description=description)
        )
    add_launch_arg("mode", "FP32", "YOLO inference mode")
    add_launch_arg("input_image","", description="input camera topic")
    add_launch_arg("camera_container_name","camera_container")
    add_launch_arg("yolo_type","", description="yolo model type")
    add_launch_arg("label_file","" ,description="tensorrt node label file")
    add_launch_arg("gpu_id","", description="gpu setting")
    add_launch_arg("output_topic", "camera0/rois0", "YOLO output topic")
    add_launch_arg("use_intra_process", "", "use intra process")
    add_launch_arg("use_multithread", "", "use multithread")
    add_launch_arg("camera_model_param_path")
    add_launch_arg("rorate_config_path", "", description="rotate configuration file path")

    set_container_executable = SetLaunchConfiguration(
        "container_executable",
        "component_container",
        condition=UnlessCondition(LaunchConfiguration("use_multithread")),
    )

    set_container_mt_executable = SetLaunchConfiguration(
        "container_executable",
        "component_container_mt",
        condition=IfCondition(LaunchConfiguration("use_multithread")),
    )

    return launch.LaunchDescription(
        launch_arguments
        + [set_container_executable, set_container_mt_executable]
        + [OpaqueFunction(function=launch_setup)]
    )
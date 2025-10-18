import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():

    # Package path
    pkg_path = get_package_share_directory('mobile_robot')
    
    # Xacro file path
    xacro_file_path = os.path.join(pkg_path, 'urdf', 'dd_bot.urdf.xacro')

    # -------- Robot Description --------
    # Use xacro to process the file
    robot_description_raw = xacro.process_file(xacro_file_path).toxml()
    
    # -------- Nodes --------
    # Gazebo Sim Node
    # This command starts the Gazebo server
    start_gazebo_server_cmd = ExecuteProcess(
        cmd=['gz', 'sim', '-s', '-r', 'empty.sdf'],
        output='screen'
    )

    # This command starts the Gazebo client GUI
    start_gazebo_client_cmd = ExecuteProcess(
        cmd=['gz', 'sim', '-g'],
        output='screen'
    )

    # Robot State Publisher Node
    # This publishes the robot's state (TF frames) to ROS 2
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw,
                     'use_sim_time': True}]
    )
    
    # Spawn Entity Node
    # This command spawns the robot model into the Gazebo simulation
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-entity', 'dd_bot'],
        output='screen'
    )

    # ROS <-> GZ Bridge
    # This bridge is essential for communication between ROS 2 and Gazebo
    # It bridges the ROS 2 /cmd_vel topic to the Gazebo topic /model/dd_bot/cmd_vel
    '''bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
        output='screen'
    )'''

    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Bridge cmd_vel (ROS2 → Gazebo)
            '/model/dd_bot/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',

            # Bridge odometry (Gazebo → ROS2)
            '/model/dd_bot/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry',

            # Bridge clock (Gazebo → ROS2)
            '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock'
        ],
        output='screen'
    )

    return LaunchDescription([
        start_gazebo_server_cmd,
        start_gazebo_client_cmd,
        robot_state_publisher_node,
        spawn_entity_node,
        bridge_node
    ])
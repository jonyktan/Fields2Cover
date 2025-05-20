# Build ROS 2 action server

1. Enter ROS workspace.

    ```
    cd ~/ros2_ws
    ```

1. Build ROS package

    ```
    colcon build
    ```

1. Source workspace.

    ```
    . install/setup.bash
    ```

# Get coverage path

1. Run action server.

    ```
    ros2 run coverage_path_generator coverage_path_server
    ```

1. Send action request. Example provided:

    ```
    ros2 action send_goal /coverage_path_action custom_interfaces/action/CoveragePathAction "{robot_width_m: 3.0, robot_operational_width_m: 5.0, robot_min_turning_radius_m: 0, robot_cruise_velocity_ms: 3, robot_turn_velocity_ms: 1, field: [{x: 10, y: 10}, {x: 10, y: 50}, {x: 90, y: 50}, {x: 90, y: 10}], swath_objective: "swath_length", route_pattern: "snake", path_turns_type: "reeds_shepp_continuous"}"
    ```

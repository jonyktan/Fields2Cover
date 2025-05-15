# Build ROS 2 action server

1. Enter ROS workspace.

    ```
    cd ~/ros2_ws
    ```

1. Build ROS package

    ```
    colcon build --packages-select coverage_path_generator
    ```

1. Source workspace.

    ```
    . install/setup.bash
    ```
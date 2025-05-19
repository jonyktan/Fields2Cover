import rclpy
from rclpy import ActionServer
from rclpy.node import Node

from action import CoveragePathAction

import fields2cover as f2c

class CoveragePathGenerator(Node):
    def __init__(self):
        super().__init__('coverage_path_server')# Specify default node name

        # Get the parameters from servers_launch.yaml (can also be passed in CLI)
        # Declare the parameters for describing robots
        self.declare_parameter("robot_width_m", 3.0) # Default to 3.0m
        self.declare_parameter("robot_operational_width_m", 10.0) # Default to 10.0m
        self.declare_parameter("robot_min_turning_radius_m", 0.0) # Default to 0.0m (quadrotor)
        self.declare_parameter("robot_cruise_velocity_ms", 3.0) # Default to 3.0m/s
        self.declare_parameter("robot_turn_velocity_ms", 1.0) # Default to 1.0m/s
        self.robot_width_m = self.get_parameter("robot_width_m").value
        self.robot_operational_width_m = self.get_parameter("robot_operational_width_m").value
        self.robot_min_turning_radius_m = self.get_parameter("robot_min_turning_radius_m").value
        self.robot_cruise_velocity_ms = self.get_parameter("robot_cruise_velocity_ms").value
        self.robot_turn_velocity_ms = self.get_parameter("robot_turn_velocity_ms").value

        # Create robot
        robot = f2c.Robot(self.robot_width_m, self.robot_operational_width_m)
        robot.setMinTurningRadius(self.robot_min_turning_radius_m)
        robot.setCruiseVel(self.robot_cruise_velocity_ms)
        robot.setTurnVel(self.robot_turn_velocity_ms)
        # TODO: (?) Print out selected param values

        # Action server
        self._action_server = ActionServer(
            self,
            action_type=CoveragePathAction,
            action_name='coverage_path_action',
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            # callback_group=action_cb_group
            )
        self.action_result = self.CoveragePathAction.Result()

def main():
    print('Hi from coverage_path_generator.')


if __name__ == '__main__':
    main()

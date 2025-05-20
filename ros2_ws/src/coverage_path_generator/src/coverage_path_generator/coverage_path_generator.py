import logging

import rclpy
from rclpy.action import ActionServer, CancelResponse
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

import action
from action import CoveragePathAction

import fields2cover as f2c

class CoveragePathGenerator(Node):
    """Class for ROS2 node handling coverage path generation action."""
    def __init__(self):
        super().__init__('coverage_path_server')# Specify default node name

        # Get the parameters from servers_launch.yaml (can also be passed in CLI)
        # # Declare the parameters for describing robots
        # self.declare_parameter("robot_width_m", 3.0) # Default to 3.0m
        # self.robot_width_m = self.get_parameter("robot_width_m").value
        
        # Action server
        self._action_server = ActionServer(
            self,
            action_type=CoveragePathAction,
            action_name='coverage_path_action',
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            # callback_group=action_cb_group
            )
        self.action_result = CoveragePathAction.Result()

    def execute_callback(self, goal_handle):
        """Callback upon receipt of request at action topic."""
        
        # Create robot
        robot = f2c.Robot(goal_handle.robot_width_m, goal_handle.robot_operational_width_m)
        robot.setMinTurningRadius(goal_handle.robot_min_turning_radius_m)
        robot.setCruiseVel(goal_handle.robot_cruise_velocity_ms)
        robot.setTurnVel(goal_handle.robot_turn_velocity_ms)
        # TODO: (?) Print out selected param values

        # Get field from xml
        field = f2c.Parser().importFieldGml(DATA_PATH + "test1.xml") # TODO: Update this to get field from request
        # Transform to UTM
        f2c.Transform.transformToUTM(field)

        # TODO: Decompose field if more efficient (https://fields2cover.github.io/source/tutorials/decomposition.html)
        
        # Create (constant) headland around the field(s)
        const_hl = f2c.HG_Const_gen()
        no_hl = const_hl.generateHeadlands(field.getField(), 3.0 * robot.getWidth())
        print("The complete area is ", field.getField().area(),
              ", and the area without headlands is ", no_hl.area())

        # # Plan route using metaheuristics
        # mid_hl = const_hl.generateHeadlands(field.getField(), 1.5 * robot.getWidth())
        # route_planner = f2c.RP_RoutePlannerBase()
        # route = route_planner.genRoute(mid_hl, swaths)
        # route_planner.setStartAndEndPoint()

        # Set objective function for swath generation (https://fields2cover.github.io/source/tutorials/swath_generator.html)
        match goal_handle.request.swath_objective:
            case "swath_length":
                swath_obj = f2c.OBJ_SwathLength()
            case "num_swath":
                swath_obj = f2c.OBJ_NSwath()
            case "custom_angle":
                swath_obj = goal_handle.request.custom_angle_rad # e.g. math.pi
        # Generate swaths using brute force method
        bf_sw_gen = f2c.SG_BruteForce()
        swaths = bf_sw_gen.generateBestSwaths(swath_obj, robot.getCovWidth(), no_hl.getGeometry(0))

        # Set pattern for route planning (https://fields2cover.github.io/source/tutorials/route_planning.html)
        match goal_handle.request.route_pattern:
            case "boustrophedon":
                swath_sorter = f2c.RP_Boustrophedon()
            case "snake":
                swath_sorter = f2c.RP_Snake()
            case "spiral":
                swath_sorter = f2c.RP_Spiral()
            case "custom_order":
                swath_sorter = f2c.RP_CustomOrder(goal_handle.request.custom_order)
        # Generate route using pattern
        swaths = swath_sorter.genSortedSwaths(swaths)
        
        # Set curve type for path planning (https://fields2cover.github.io/source/tutorials/path_planning.html)
        path_planner = f2c.PP_PathPlanning()
        match goal_handle.request.path_turns_type:
            case "dubins":
                path_arg = f2c.PP_DubinsCurves()
            case "dubins_continuous":
                path_arg = f2c.PP_DubinsCurvesCC()
            case "reeds_shepp":
                path_arg = f2c.PP_ReedsSheppCurves()
            case "reeds_shepp_continuous":
                path_arg = f2c.PP_ReedsSheppCurvesHC()
        # Generate path
        path = path_planner.planPath(robot, swaths, path_arg)

        goal_handle.succeed()
        path_result = CoveragePathAction.Result()
        path_result.path = path
        return path_result

    def _send_feedback(self, goal_handle, feedback_string):
        """Publish feedback message to action client."""

        feedback_msg = CoveragePathAction.Feedback()
        feedback_msg.feedback_msg = feedback_string
 
        # Printout
        self.get_logger().debug(f"Feedback: {feedback_msg.feedback_msg}")
        
        # Publish feedback
        goal_handle.publish_feedback(feedback_msg)

    def cancel_callback(self, goal_handle):
        """Custom cancel callback as the default is "No cancellations"."""

        self.get_logger().info(f"Cancel request accepted.")
        return CancelResponse.ACCEPT

        # TODO: implement logic to check whether to accept cancellation
        # self.get_logger().info(f"Cancel request rejected.")
        # return CancelResponse.REJECT



def main(args=None):
    print('Hi from coverage_path_generator.')

    rclpy.init(args=args)

    coverage_path_server = CoveragePathGenerator()
    executor = MultiThreadedExecutor()
    executor.add_node(coverage_path_server)

    try:
        while rclpy.ok():
            executor.spin_once(timeout_sec=0.01)

    except KeyboardInterrupt:
        logging.warning("Keyboard interrupt received")
        raise
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}", exc_info=True)
    finally:
        if rclpy.ok():
            logging.info("Shutting down ROS2...")
            coverage_path_server.destroy_node()
            rclpy.shutdown()
        else:
            logging.warning("ROS2 was not initialized or already shut down.")



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received in __main__. Graceful shutdown initiated.")
    except Exception as e:
        logging.error(f"Unexpected error in main execution: {e}", exc_info=True)
    finally:
        logging.info("Program terminated")
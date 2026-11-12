import math
import time
import threading

import rclpy
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_move_interfaces.action import MoveToGoal


class TurtleMoveServer(Node):

    def __init__(self):
        super().__init__('turtle_move_server')

        self.current_pose = None
        self.goal_active = False
        self.goal_lock = threading.Lock()

        self.callback_group = ReentrantCallbackGroup()

        self.velocity_publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.pose_subscriber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.callback_group
        )

        self.action_server = ActionServer(
            self,
            MoveToGoal,
            'move_to_goal',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('Turtle Move Action Server started.')

    def pose_callback(self, msg):
        self.current_pose = msg

    def goal_callback(self, goal_request):
        x = goal_request.target_x
        y = goal_request.target_y

        if not (
            math.isfinite(x)
            and math.isfinite(y)
            and 0.5 <= x <= 10.5
            and 0.5 <= y <= 10.5
        ):
            self.get_logger().warn('Invalid target position.')
            return GoalResponse.REJECT

        with self.goal_lock:
            if self.goal_active:
                self.get_logger().warn('Another goal is active.')
                return GoalResponse.REJECT

            self.goal_active = True

        self.get_logger().info(
            f'Goal received: ({x:.2f}, {y:.2f})'
        )

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received.')
        return CancelResponse.ACCEPT

    def stop_turtle(self):
        self.velocity_publisher.publish(Twist())

    def execute_callback(self, goal_handle):
        target_x = goal_handle.request.target_x
        target_y = goal_handle.request.target_y

        feedback = MoveToGoal.Feedback()
        result = MoveToGoal.Result()

        result.success = False
        start_time = time.monotonic()

        self.get_logger().info('Moving to target...')

        try:
            while rclpy.ok():

                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    self.get_logger().info('Goal canceled.')
                    break

                if time.monotonic() - start_time >= 60.0:
                    goal_handle.abort()
                    self.get_logger().warn('Goal timeout.')
                    break

                if self.current_pose is None:
                    time.sleep(0.1)
                    continue

                x = self.current_pose.x
                y = self.current_pose.y
                theta = self.current_pose.theta

                dx = target_x - x
                dy = target_y - y

                distance = math.hypot(dx, dy)

                target_angle = math.atan2(dy, dx)

                angle_error = math.atan2(
                    math.sin(target_angle - theta),
                    math.cos(target_angle - theta)
                )

                feedback.current_x = x
                feedback.current_y = y
                feedback.distance_remaining = distance

                goal_handle.publish_feedback(feedback)

                if distance < 0.15:
                    self.stop_turtle()
                    goal_handle.succeed()
                    result.success = True
                    self.get_logger().info('Goal reached.')
                    break

                cmd = Twist()

                if abs(angle_error) > 0.35:
                    cmd.linear.x = 0.0
                else:
                    cmd.linear.x = min(1.5, distance)

                cmd.angular.z = max(
                    -2.0,
                    min(2.0, 4.0 * angle_error)
                )

                self.velocity_publisher.publish(cmd)

                time.sleep(0.1)

            if goal_handle.is_active:
                goal_handle.abort()

        finally:
            self.stop_turtle()

            if self.current_pose is not None:
                result.final_x = self.current_pose.x
                result.final_y = self.current_pose.y

            with self.goal_lock:
                self.goal_active = False

        return result


def main(args=None):
    rclpy.init(args=args)

    node = TurtleMoveServer()

    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_turtle()
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

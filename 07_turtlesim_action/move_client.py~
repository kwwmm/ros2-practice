import argparse
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from action_msgs.msg import GoalStatus
from turtle_move_interfaces.action import MoveToGoal


class TurtleMoveClient(Node):

    def __init__(self, cancel_after=0.0):
        super().__init__('turtle_move_client')

        self.action_client = ActionClient(
            self,
            MoveToGoal,
            'move_to_goal'
        )

        self.goal_handle = None
        self.finished = False

        self.cancel_after = cancel_after
        self.cancel_sent = False
        self.start_time = None

    def send_goal(self, x, y):
        goal_msg = MoveToGoal.Goal()

        goal_msg.target_x = float(x)
        goal_msg.target_y = float(y)

        self.get_logger().info('Waiting for Action Server...')

        self.action_client.wait_for_server()

        self.start_time = time.monotonic()

        self.send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self.send_goal_future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):
        self.goal_handle = future.result()

        if not self.goal_handle.accepted:
            self.get_logger().warn('Goal rejected.')
            self.finished = True
            return

        self.get_logger().info('Goal accepted.')

        self.result_future = self.goal_handle.get_result_async()

        self.result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback

        self.get_logger().info(
            f'Position: ({feedback.current_x:.2f}, '
            f'{feedback.current_y:.2f}) | '
            f'Distance: {feedback.distance_remaining:.2f}'
        )

        if (
            self.cancel_after > 0
            and not self.cancel_sent
            and self.goal_handle is not None
            and time.monotonic() - self.start_time
            >= self.cancel_after
        ):
            self.cancel_sent = True

            self.get_logger().info('Sending cancel request...')

            cancel_future = self.goal_handle.cancel_goal_async()

            cancel_future.add_done_callback(
                self.cancel_response_callback
            )

    def cancel_response_callback(self, future):
        response = future.result()

        if response.goals_canceling:
            self.get_logger().info('Cancel accepted.')
        else:
            self.get_logger().warn('Cancel not accepted.')

    def result_callback(self, future):
        response = future.result()

        result = response.result
        status = response.status

        self.get_logger().info(
            f'Final position: '
            f'({result.final_x:.2f}, {result.final_y:.2f})'
        )

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Goal succeeded.')

        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info('Goal canceled.')

        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().warn('Goal aborted.')

        else:
            self.get_logger().warn(f'Goal status: {status}')

        self.finished = True


def main(args=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('x', type=float)
    parser.add_argument('y', type=float)

    parser.add_argument(
        '--cancel-after',
        type=float,
        default=0.0
    )

    parsed_args = parser.parse_args()

    rclpy.init(args=args)

    node = TurtleMoveClient(
        cancel_after=parsed_args.cancel_after
    )

    try:
        node.send_goal(parsed_args.x, parsed_args.y)

        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.1)

    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

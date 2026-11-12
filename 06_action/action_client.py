
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from action_msgs.msg import GoalStatus
from action_tutorials_interfaces.action import Fibonacci


class FibonacciActionClient(Node):

    def __init__(self):
        super().__init__('fibonacci_action_client')

        self.action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci'
        )

        self.goal_handle = None
        self.feedback_count = 0
        self.cancel_after = 0
        self.cancel_sent = False

    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self.get_logger().info('Waiting for Action Server...')

        self.action_client.wait_for_server()

        self.get_logger().info(f'Sending goal: {order}')

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
            self.get_logger().info('Goal rejected.')
            return

        self.get_logger().info('Goal accepted.')

        self.result_future = self.goal_handle.get_result_async()

        self.result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback

        self.feedback_count += 1

        self.get_logger().info(
            f'Feedback: {feedback.partial_sequence}'
        )

        if (
            self.cancel_after > 0
            and self.feedback_count >= self.cancel_after
            and not self.cancel_sent
            and self.goal_handle is not None
        ):
            self.cancel_sent = True

            self.get_logger().info('Requesting cancellation...')

            self.cancel_future = self.goal_handle.cancel_goal_async()

            self.cancel_future.add_done_callback(
                self.cancel_response_callback
            )

    def cancel_response_callback(self, future):
        response = future.result()

        if response.goals_canceling:
            self.get_logger().info('Cancel request accepted.')
        else:
            self.get_logger().info('Cancel request not accepted.')

    def result_callback(self, future):
        response = future.result()

        result = response.result
        status = response.status

        self.get_logger().info(f'Result: {result.sequence}')

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Goal succeeded.')

        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info('Goal canceled.')

        else:
            self.get_logger().info(f'Goal status: {status}')


def main(args=None):
    rclpy.init(args=args)

    node = FibonacciActionClient()

    try:
        node.send_goal(10)
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

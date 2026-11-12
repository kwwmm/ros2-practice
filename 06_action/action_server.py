
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from action_tutorials_interfaces.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')

        self.action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup()
        )

        self.get_logger().info('Action Server started.')

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received.')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        order = goal_handle.request.order

        result = Fibonacci.Result()

        if order <= 0:
            result.sequence = []
            goal_handle.succeed()
            return result

        if order == 1:
            result.sequence = [0]
            goal_handle.succeed()
            return result

        for i in range(2, order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.sequence = feedback_msg.partial_sequence
                self.get_logger().info('Goal canceled.')
                return result

            next_number = (
                feedback_msg.partial_sequence[i - 1]
                + feedback_msg.partial_sequence[i - 2]
            )

            feedback_msg.partial_sequence.append(next_number)

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'Feedback: {feedback_msg.partial_sequence}'
            )

            time.sleep(1.0)

        goal_handle.succeed()

        result.sequence = feedback_msg.partial_sequence

        self.get_logger().info('Goal succeeded.')

        return result


def main(args=None):
    rclpy.init(args=args)

    node = FibonacciActionServer()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

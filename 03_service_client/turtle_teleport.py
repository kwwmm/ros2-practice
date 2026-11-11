
import sys

import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute


class TurtleTeleportClient(Node):

    def __init__(self):
        super().__init__('turtle_teleport_client')

        self.client = self.create_client(
            TeleportAbsolute,
            '/turtle1/teleport_absolute'
        )

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')

    def send_request(self, x, y, theta):
        request = TeleportAbsolute.Request()

        request.x = x
        request.y = y
        request.theta = theta

        future = self.client.call_async(request)

        rclpy.spin_until_future_complete(self, future)

        return future.result()


def main():
    if len(sys.argv) != 4:
        print('Usage: python3 turtle_teleport.py x y theta')
        return

    rclpy.init()

    node = TurtleTeleportClient()

    x = float(sys.argv[1])
    y = float(sys.argv[2])
    theta = float(sys.argv[3])

    response = node.send_request(x, y, theta)

    if response is not None:
        node.get_logger().info(
            f'Turtle moved to x={x}, y={y}, theta={theta}'
        )
    else:
        node.get_logger().error('Service call failed')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

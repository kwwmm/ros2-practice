
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class TurtlePose(Node):
    def __init__(self):
        super().__init__('turtle_pose_reader')

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

    def pose_callback(self, msg):
        self.get_logger().info(
            f'X: {msg.x:.2f}, '
            f'Y: {msg.y:.2f}, '
            f'Theta: {msg.theta:.2f}'
        )


def main():
    rclpy.init()
    node = TurtlePose()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

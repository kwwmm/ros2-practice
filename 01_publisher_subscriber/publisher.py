
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class PublisherNode(Node):
    def __init__(self):
        super().__init__('my_publisher')

        self.publisher_ = self.create_publisher(
            String,
            'my_topic',
            10
        )

        self.timer = self.create_timer(1.0, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS2! Count: {self.count}'

        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')

        self.count += 1


def main():
    rclpy.init()

    node = PublisherNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

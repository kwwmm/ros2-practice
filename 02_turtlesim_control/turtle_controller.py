
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')

        # Publisher: send velocity commands
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Publish every 0.1 seconds
        self.timer = self.create_timer(
            0.1,
            self.move_turtle
        )

    def move_turtle(self):
        msg = Twist()

        # Linear velocity
        msg.linear.x = 2.0

        # Angular velocity
        msg.angular.z = 1.0

        self.publisher.publish(msg)

    def stop_turtle(self):
        self.publisher.publish(Twist())


def main():
    rclpy.init()
    node = TurtleController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_turtle()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

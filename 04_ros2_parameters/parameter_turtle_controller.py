
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult


class ParameterTurtleController(Node):

    def __init__(self):
        super().__init__('parameter_turtle_controller')

        # Declare parameters with default values
        self.declare_parameter('linear_speed', 2.0)
        self.declare_parameter('angular_speed', 1.0)

        # Create a publisher for turtle velocity commands
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Register a callback to validate parameter changes
        self.add_on_set_parameters_callback(self.validate_parameters)

        # Publish velocity commands every 0.1 seconds
        self.timer = self.create_timer(0.1, self.timer_callback)

        self.get_logger().info('Parameter turtle controller started.')

    def validate_parameters(self, parameters):
        for parameter in parameters:
            if parameter.name in ('linear_speed', 'angular_speed'):

                if parameter.type_ != Parameter.Type.DOUBLE:
                    return SetParametersResult(
                        successful=False,
                        reason=f'{parameter.name} must be a double.'
                    )

                if not 0.0 < parameter.value <= 5.0:
                    return SetParametersResult(
                        successful=False,
                        reason=f'{parameter.name} must be greater than 0.0 and at most 5.0.'
                    )

        return SetParametersResult(successful=True)

    def timer_callback(self):
        linear_speed = self.get_parameter('linear_speed').value
        angular_speed = self.get_parameter('angular_speed').value

        msg = Twist()
        msg.linear.x = linear_speed
        msg.angular.z = angular_speed

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = ParameterTurtleController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

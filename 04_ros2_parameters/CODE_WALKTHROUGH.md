# 실습 04 — ROS2 Parameters & Dynamic Control: 코드 상세 분석

## 1. Python 전체 코드

`parameter_turtle_controller.py`는 **77줄**로 구성되어 있다(빈 줄·주석 포함). 먼저 전체 코드를 읽고, 아래에서 실제 행 번호를 기준으로 `import` → 클래스 생성 → 파라미터 검사 → Timer Callback → `main()` 순서로 살펴본다.

```python
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
```

**코드에서 주목할 연결:** `create_timer(0.1, self.timer_callback)`이 호출할 함수를 등록하고, `timer_callback()`은 매번 `get_parameter()`로 값을 가져와 `Twist`를 발행한다. 한편 `add_on_set_parameters_callback(self.validate_parameters)`은 변경 요청을 받았을 때만 검사 함수를 실행한다.

---

## 2. `import` 다섯 줄: 무엇을 가져오는가?

### 2.1 1행 — `import rclpy`

- `import`: Python 모듈을 현재 파일에서 사용할 수 있도록 가져오는 키워드.
- `rclpy`: ROS2의 Python 클라이언트 라이브러리. ROS2 초기화, 노드 실행, 종료 등을 담당한다.
- 이 코드는 이후 `rclpy.init()`, `rclpy.spin()`, `rclpy.ok()`, `rclpy.shutdown()`에서 이 이름을 사용한다.
- 일반 Python의 모든 프로그램에 필요한 모듈은 아니다. **ROS2 Python 노드를 작성하기 때문에** 필요하다.

### 2.2 2행 — `from rclpy.node import Node`

- `from 패키지.모듈 import 이름`: 특정 모듈에서 필요한 이름만 가져오는 문법.
- `Node`: ROS2 노드를 표현하는 기반 클래스.
- `class ParameterTurtleController(Node)`에서 상속받을 부모 클래스다.
- 상속 덕분에 자식 클래스에서 `create_publisher()`, `create_timer()`, `get_parameter()` 등의 노드 메서드를 사용할 수 있다.

### 2.3 3행 — `from rclpy.parameter import Parameter`

- `Parameter`: 파라미터의 이름, 값, 타입을 표현하는 Python 클래스.
- 이 파일에서는 **파라미터 인스턴스를 직접 새로 생성하지는 않는다.**
- 대신 `Parameter.Type.DOUBLE`이라는 타입 열거형(enum)을 사용해 전달받은 값이 실수형 파라미터인지 확인한다.
- 이 파일의 `parameter`는 파이썬 함수 인자 이름이기도 하므로, `Parameter`(클래스)와 `parameter`(각 검사 대상 객체)를 구분한다.

### 2.4 4행 — `from geometry_msgs.msg import Twist`

- `geometry_msgs`: ROS2에서 널리 사용하는 기하학적 메시지 패키지.
- `Twist`: 선속도와 각속도를 함께 담는 메시지 타입.
- `msg = Twist()`는 메시지 객체 생성이며, `self.create_publisher(Twist, ...)`의 `Twist`는 발행할 **메시지 타입 자체**를 의미한다.
- `Twist.linear`와 `Twist.angular`은 각각 3차원 벡터 구조다. 여기서는 `linear.x`와 `angular.z`만 설정하고, 다른 값은 기본값 `0.0`으로 둔다.

### 2.5 5행 — `from rcl_interfaces.msg import SetParametersResult`

- `rcl_interfaces`: ROS2 파라미터 관련 인터페이스를 포함하는 패키지.
- `SetParametersResult`: 파라미터 설정 요청의 **허용 여부**와 **거부 이유**를 표현하는 메시지.
- 주요 필드는 `successful: bool`, `reason: str`이다.
- 콜백에서 `return True`가 아니라 `return SetParametersResult(successful=True)`를 사용하는 이유다.

> **Python 개념:** `import rclpy`는 모듈 전체를 이름으로 가져오므로 `rclpy.init()`처럼 쓰고, `from ... import Twist`는 `Twist()`처럼 바로 쓴다.

---

---

## 3. 클래스와 생성자: 노드가 만들어지는 과정 (8~30행)

### 3.1 8행 — `class ParameterTurtleController(Node):`

- `class`는 새로운 클래스를 정의하는 Python 키워드다.
- `ParameterTurtleController`는 사용자가 정의한 클래스 이름이다. 관례상 클래스명은 대문자로 단어를 구분하는 `PascalCase`를 사용한다.
- `(Node)`는 `Node` 클래스를 상속받는다는 뜻이다.
- 콜론(`:`) 다음에 들여쓰기된 영역이 클래스 본문이다.
- **주의:** 이 클래스 정의 문장을 만났다고 즉시 ROS2 노드가 생성되는 것은 아니다. 실제 객체는 64행 `ParameterTurtleController()`에서 생성된다.

### 3.2 10행 — `def __init__(self):`

- `def`: 함수를 정의하는 키워드.
- `__init__`: 객체가 생성될 때 초기 설정을 담당하는 특수 메서드.
- `self`: 현재 생성된 **그 객체 자신을 참조**하는 첫 번째 인자. Python이 인스턴스 메서드를 호출할 때 자동으로 전달한다.
- `self`는 Python 예약어가 아니라 강한 관례지만, 일반적으로 반드시 그대로 사용한다.
- 이 함수에서는 파라미터 선언, Publisher 생성, Callback 등록, Timer 생성이 순서대로 실행된다.

예를 들어 64행의 `node = ParameterTurtleController()`가 실행되면 Python은 새 객체를 만들고 해당 객체를 대상으로 `__init__`를 실행한다. 이때 `self`가 그 새 객체를 가리킨다.

### 3.3 11행 — `super().__init__('parameter_turtle_controller')`

- `super()`는 부모 클래스(`Node`)의 메서드에 접근하기 위한 기능이다.
- `super().__init__(...)`은 **ROS2 Node의 초기화**를 먼저 수행한다.
- 문자열 `'parameter_turtle_controller'`는 ROS2 그래프에 표시될 노드 이름이다.
- 부모 초기화를 생략하면 정상적인 ROS2 Node 기반 상태가 만들어지지 않으므로 이어지는 파라미터/Publisher/Timer API를 올바르게 사용할 수 없다.
- **노드 이름과 클래스 이름은 별개:** `ParameterTurtleController`는 Python 클래스명이고 `/parameter_turtle_controller`는 ROS2 노드명이다.

### 3.4 13~15행 — 기본 Parameter 선언

```python
# Declare parameters with default values
self.declare_parameter('linear_speed', 2.0)
self.declare_parameter('angular_speed', 1.0)
```

- `#`으로 시작하는 줄은 Python **주석**이며 실행되지 않는다.
- `self.`는 현재 노드 객체의 메서드에 접근한다는 뜻이다.
- `declare_parameter(name, value)`의 첫 번째 인자는 이름(`str`), 두 번째 인자는 기본값이다.
- `linear_speed`의 초기값은 `2.0`, `angular_speed`의 초기값은 `1.0`이다.
- `2.0`, `1.0`은 소수점을 가진 Python `float` 값이므로 ROS2에서는 **double 파라미터**로 다뤄진다.
- ROS2에서 파라미터는 선언된 뒤 `get_parameter()`로 읽을 수 있다. 이 실습에서는 생성자에서 초기 선언을 완료한 뒤 Timer를 시작한다.

| 이름 | 기본값 | 허용 타입 | 코드가 허용하는 값 |
|---|---:|---|---|
| `linear_speed` | `2.0` | `DOUBLE` | `0.0 < 값 <= 5.0` |
| `angular_speed` | `1.0` | `DOUBLE` | `0.0 < 값 <= 5.0` |

**핵심:** 기본값을 선언한다는 것은 단순히 로컬 변수 `linear_speed = 2.0`을 만드는 것과 다르다. ROS2 노드의 파라미터 저장소에 이름과 타입을 갖는 설정으로 등록하므로 CLI에서 조회·변경할 수 있다.

### 3.5 17~22행 — Publisher 만들기

```python
self.publisher = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

- `self.create_publisher(...)`: 부모 `Node`가 제공하는 Publisher 생성 메서드.
- 첫 번째 인자 `Twist`: 발행할 ROS2 메시지의 타입이다. `Twist()`와 달리 괄호가 없으므로 **클래스/타입**을 전달한다.
- 두 번째 인자 `'/turtle1/cmd_vel'`: Topic의 전체 이름. 첫 글자 `/`는 절대 Topic 이름임을 뜻한다.
- 세 번째 인자 `10`: 정수 QoS 깊이(depth) 지정. 이 간단한 형태는 ROS2 기본 QoS 프로파일을 기반으로 메시지 기록 보관 개수를 10으로 설정한다.
- 반환값은 Publisher 객체이며 `self.publisher`라는 **인스턴스 속성**으로 보관한다.
- 여러 줄로 나누고 괄호 안에 인자를 적어도, Python 입장에서는 하나의 함수 호출이다. 쉼표(`,`)는 인자를 구분한다.

이 시점에 Publisher 통신 객체가 준비되지만 **이 코드 자체는 아직 속도 메시지를 발행하지 않는다.** 실제 발행은 58행에서 일어난다.

### 3.6 24~25행 — 변경 검증 Callback 등록

```python
self.add_on_set_parameters_callback(self.validate_parameters)
```

- `add_on_set_parameters_callback(...)`: ROS2에서 파라미터 설정 시 검증용으로 실행할 함수를 등록한다.
- `self.validate_parameters`: 메서드 **참조**다. 괄호가 없으므로 지금 실행하지 않는다.
- `self.validate_parameters()`로 바꾸면 그 자리에서 인자 없이 함수를 호출하려 하기 때문에 오류가 발생한다.
- 나중에 설정 요청이 들어오면 ROS2가 등록된 콜백을 호출하고 **변경하려는 파라미터들의 목록**을 전달한다.
- 콜백이 `SetParametersResult(successful=False, ...)`를 반환하면 해당 설정 요청은 거부된다.

### 3.7 27~28행 — 주기적 Timer 등록

```python
self.timer = self.create_timer(0.1, self.timer_callback)
```

- `create_timer(period, callback)`의 첫 인자 `0.1`은 **초(second)** 단위 주기다.
- `0.1초`는 이론적으로 `1 / 0.1 = 10 Hz`에 해당한다.
- `self.timer_callback`도 괄호가 없는 **함수 참조**이며, 타이머가 준비될 때 실행할 함수로 등록된다.
- 반환값인 Timer 객체를 `self.timer`에 보관한다.
- 실제 콜백 실행은 `rclpy.spin(node)`이 Executor를 통해 준비된 작업을 처리할 때 일어난다.

### 3.8 30행 — 시작 로그

```python
self.get_logger().info('Parameter turtle controller started.')
```

- `self.get_logger()`: 현재 노드의 Logger 객체를 얻는다.
- `.info(...)`: 정보 수준 로그를 출력한다.
- 인자는 출력할 문자열이다.
- 이 로그가 보이면 적어도 생성자의 앞선 설정 코드가 예외 없이 진행되어 해당 행까지 도달했음을 알 수 있다.
- **시작 로그가 보인다고 Topic 주기나 실제 거북이 움직임까지 보장되는 것은 아니다.** 각각 별도 CLI로 검증해야 한다.

---

---

## 4. 파라미터 검증 함수 완전 분석 (32~48행)

### 4.1 32행 — 메서드 정의

```python
def validate_parameters(self, parameters):
```

- 첫 번째 인자 `self`: Controller 노드 객체.
- 두 번째 인자 `parameters`: 변경 요청을 받은 `Parameter` 객체들의 **리스트**.
- 이 메서드를 호출하는 주체는 파라미터 설정 작업을 처리하는 ROS2 측이다. 사용자가 코드에서 직접 실행하지 않아도 된다.
- 이 함수의 반환형으로 기대되는 것은 `SetParametersResult`다.

### 4.2 33~34행 — 목록 순회와 대상 구분

```python
for parameter in parameters:
    if parameter.name in ('linear_speed', 'angular_speed'):
```

- `for A in B`: 반복 가능한 자료 `B`에서 원소를 하나씩 꺼내 `A`에 넣는 반복문.
- `parameter`는 현재 검사 중인 **하나의 Parameter 객체**다.
- `parameter.name`은 해당 객체의 이름 문자열이다.
- `('linear_speed', 'angular_speed')`는 문자열 두 개를 가진 `tuple`이다. `()`와 쉼표로 작성된다.
- `in`은 해당 값이 tuple 안에 있는지 검사한다. 두 이름 중 하나라면 `True`다.
- 다른 이름의 파라미터가 전달되면 이 코드의 **사용자 정의 속도 검사**는 건너뛴다. 이것이 노드의 모든 파라미터를 무조건 허용한다는 뜻은 아니다. ROS2 자체의 선언/타입 관련 규칙도 적용된다.

### 4.3 36~40행 — 자료형 검사

```python
if parameter.type_ != Parameter.Type.DOUBLE:
    return SetParametersResult(
        successful=False,
        reason=f'{parameter.name} must be a double.'
    )
```

- `parameter.type_`: ROS2 파라미터의 타입을 나타내는 속성이다. 이름 끝 `_`도 실제 API의 일부다.
- `Parameter.Type.DOUBLE`: `double`에 해당하는 Enum 값.
- `!=`: '같지 않다'라는 비교 연산자다.
- `if`의 조건이 참이면 바로 `return`한다. 현재 함수의 나머지 검사도 실행되지 않는다.
- `SetParametersResult(...)`는 결과 메시지 **객체를 생성**한다.
- `successful=False`: 변경을 허용하지 않음.
- `reason=...`: 거부 사유를 문자열로 제공.
- `f'...'`: f-string. 중괄호 안의 `parameter.name`을 현재 이름 문자열로 치환한다.

예: `linear_speed`를 정수형으로 변경하려는 경우 검증 콜백이 그 요청을 받으면 `linear_speed must be a double.`이라는 거부 이유를 만들 수 있다. 다만 실제 CLI에서 어떤 오류가 먼저 보이는지는 ROS2 자체의 타입 검사와 요청 처리 순서에도 영향을 받는다.

### 4.4 42~46행 — 값 범위 검사

```python
if not 0.0 < parameter.value <= 5.0:
    return SetParametersResult(
        successful=False,
        reason=f'{parameter.name} must be greater than 0.0 and at most 5.0.'
    )
```

- `parameter.value`는 실제 파라미터 값이다. 이번 검사 대상에서는 실수형으로 기대한다.
- `0.0 < x <= 5.0`은 Python의 **연쇄 비교(chained comparison)** 문법으로 `0.0 < x and x <= 5.0`과 같은 조건을 표현한다.
- 앞의 `not`은 참·거짓을 반대로 뒤집는다.
- 따라서 `x = 0.0`, `x = -1.0`, `x = 6.0`은 허용하지 않는다.
- `x = 0.1`, `x = 1.0`, `x = 5.0`은 이 범위 검사 기준으로 허용한다.
- `return`이 실행되면 즉시 검사 함수가 끝나고, 설정 요청의 결과에 거부 사유가 반영된다.

실제로 사용자는 아래와 같은 출력을 확인했다.

```text
$ ros2 param set /parameter_turtle_controller linear_speed 0.0
Setting parameter failed: linear_speed must be greater than 0.0 and at most 5.0.

$ ros2 param get /parameter_turtle_controller linear_speed
Double value is: 1.0
```

이는 **잘못된 새 값이 적용되지 않았으며, 기존 값 1.0이 유지되었음**을 직접 뒷받침한다.

### 4.5 48행 — 모든 검사 통과

```python
return SetParametersResult(successful=True)
```

- 검사 대상 파라미터가 모두 앞선 조건을 통과하면 호출된다.
- `successful=True`는 파라미터 설정을 허용한다는 뜻이다.
- 여기에는 별도 `reason`을 작성하지 않았으므로 기본 문자열 값이 사용된다.
- **이 메서드가 직접 파라미터 값을 갱신하는 것은 아니다.** 검증 결과를 반환하면 ROS2의 설정 처리 과정이 성공 여부에 따라 반영한다.

### 4.6 이 함수의 실행 구조를 코드로 읽기

```text
설정 요청을 받음
    |
    v
parameters를 하나씩 순회
    |
    +-- 대상 이름이 아니면 → 사용자 정의 검사 건너뜀
    |
    +-- 자료형이 DOUBLE이 아니면 → False 반환, 종료
    |
    +-- 값이 (0.0, 5.0] 범위 밖이면 → False 반환, 종료
    |
    +-- 다음 파라미터 검사
    v
모든 검사 통과 → True 반환
```

> **Callback 시점:** `validate_parameters`는 0.1초마다 실행되는 함수가 아니다. **Parameter 설정이 시도되는 시점**에 호출된다. 반면 `timer_callback`은 주기적으로 실행된다. 두 Callback은 역할이 다르다.

---

---

## 5. Timer Callback과 `Twist` 생성 (50~58행)

### 5.1 50행 — Timer Callback 정의

```python
def timer_callback(self):
```

- `self.create_timer(0.1, self.timer_callback)`에 등록했던 메서드다.
- 주기가 되어 Timer가 준비되고 Executor가 해당 작업을 처리할 때 호출된다.
- 사용자 인자를 별도로 받지 않고, 현재 노드 객체 `self`만 전달받는다.

### 5.2 51~52행 — 그때그때 Parameter 다시 읽기

```python
linear_speed = self.get_parameter('linear_speed').value
angular_speed = self.get_parameter('angular_speed').value
```

이 두 줄이 **동적 제어의 핵심**이다.

- `get_parameter(name)`은 해당 이름의 `Parameter` 객체를 반환한다.
- `.value`는 그 객체 안에 저장된 실제 값을 읽는다.
- `linear_speed`, `angular_speed`는 이 함수가 실행될 때 만들어지는 **로컬 변수**다.
- `self.linear_speed`처럼 인스턴스에 영구 저장한 값이 아니다.
- Timer가 다음에 실행되면 두 값을 다시 가져오므로, CLI로 변경된 최신 값이 반영될 수 있다.

만약 생성자에서 값을 한 번만 읽고 Timer에서는 고정된 변수만 사용했다면, 파라미터 변경 후에도 메시지에 이전 속도가 계속 사용될 수 있다. 따라서 **값을 언제 읽느냐**가 중요하다.

### 5.3 54행 — 메시지 객체 생성

```python
msg = Twist()
```

- `Twist`는 메시지 클래스, `Twist()`는 새 메시지 인스턴스를 만드는 호출이다.
- 지역 변수 `msg`는 메시지 인스턴스를 참조한다.
- 타이머가 실행될 때마다 이 줄에서 새 객체를 만들기 때문에 이전 타이머 실행의 객체에 의존하지 않는다.
- `Twist`에는 `linear`, `angular`라는 하위 구조가 있고, 둘 다 `x`, `y`, `z` 필드를 가진다.

### 5.4 55~56행 — 속도 필드 대입

```python
msg.linear.x = linear_speed
msg.angular.z = angular_speed
```

- `=`는 Python에서 **대입 연산자**다. 오른쪽 값을 왼쪽 속성에 넣는다.
- `msg.linear.x`: 로봇 전진 방향(x축) 선속도. Turtlesim에서는 일반적으로 **단위/초** 단위로 해석한다.
- `msg.angular.z`: 평면 회전(z축 기준) 각속도, **라디안/초**로 해석한다.
- `linear.y`, `linear.z`, `angular.x`, `angular.y`에는 별도 값을 넣지 않았으므로 기본값 `0.0`으로 남는다.
- 현재 코드는 오직 **전진하면서 회전하는 평면 이동** 명령을 만든다.

파라미터를 `1.0`, `3.0`으로 변경했을 때 사용자가 실제로 관찰한 메시지는 다음과 같다.

```yaml
linear:
  x: 1.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 3.0
```

### 5.5 58행 — Publisher로 메시지 전송

```python
self.publisher.publish(msg)
```

- `self.publisher`는 생성자에서 만들어 저장한 Publisher 객체다.
- `.publish(msg)`는 `Twist` 메시지를 `/turtle1/cmd_vel` Topic에 발행한다.
- 메시지를 받는 주체는 별도 프로세스의 Turtlesim 노드다.
- Topic 통신은 비동기적인 데이터 흐름으로, `publish()` 호출 직후 Turtlesim 화면이 반드시 즉시 갱신되었다고 단정할 수 없다.

### 5.6 원형 궤적과 속도 관계

평면에서 일정한 전진 선속도 `v`와 일정한 각속도 `ω`로 이동하면, 이상적인 회전 반지름은 다음과 같이 표현할 수 있다.

$$
r = \frac{v}{|\omega|}
$$

- 초기값: `v=2.0`, `ω=1.0` → `r=2.0`.
- 변경값: `v=1.0`, `ω=3.0` → `r≈0.333`.

즉 변경 후 회전 반경이 작아질 것으로 **예상**한다. 다만 사용자가 제공한 검증 로그는 속도 **메시지의 값**을 증명하며, 화면에서 실제 반지름을 측정했다는 근거는 아니다. Turtlesim 화면 경계에 닿으면 눈에 보이는 궤적도 달라질 수 있다.

---

---

## 6. `main()`과 프로그램 시작·종료 (61~77행)

### 6.1 61행 — `def main(args=None):`

- `main`은 프로그램의 진입 흐름을 모아 둔 일반 함수 이름이다. Python의 특별한 예약 함수는 아니다.
- `args=None`은 **기본 인자(default argument)**이며 호출자가 값을 전달하지 않으면 `None`을 사용한다.
- `None`은 Python에서 값이 없음을 나타내는 객체다.
- `rclpy.init(args=args)`로 그대로 전달해 ROS2 초기화 인자에 활용한다.

### 6.2 62행 — `rclpy.init(args=args)`

- ROS2 Python 라이브러리의 컨텍스트를 초기화한다.
- 이후 Node를 생성하고 ROS2 통신을 사용할 준비를 한다.
- 일반적으로 Node를 생성하기 전에 호출해야 한다.

### 6.3 64행 — `node = ParameterTurtleController()`

- 괄호 `()`는 사용자 클래스의 **인스턴스 생성**을 요청한다.
- 생성된 객체가 `node`라는 로컬 변수에 저장된다.
- 이때 `ParameterTurtleController.__init__()`가 실행되며, 파라미터/Publisher/Timer 설정이 이루어진다.
- `node`는 이후 `spin()`과 `destroy_node()`에서 동일한 인스턴스를 가리킨다.

### 6.4 66~67행 — `try`와 `rclpy.spin(node)`

```python
try:
    rclpy.spin(node)
```

- `try`: 실행 중 발생할 수 있는 예외를 처리하기 위한 영역.
- `rclpy.spin(node)`: 노드를 Executor에 연결하여 Timer, 파라미터 관련 요청 등의 콜백을 처리할 수 있도록 실행 상태를 유지한다.
- `spin()`은 일반적으로 종료되거나 중단될 때까지 계속 실행되는 **블로킹 호출**이다.
- Timer를 `create_timer()`로 등록해 두기만 하고 `spin()`하지 않으면, 일반적인 이 실행 방식에서는 콜백이 반복 실행되지 않는다.

### 6.5 68~69행 — Ctrl+C 처리

```python
except KeyboardInterrupt:
    pass
```

- `except KeyboardInterrupt`: Ctrl+C에 따른 Python 키보드 중단 예외를 잡는다.
- `pass`: 아무 명령도 하지 않는 문장이다. 이 분기에서는 별도의 메시지를 출력하지 않는다.
- Ctrl+C 관련 종료 동작은 실행 환경과 ROS2 신호 처리에도 영향을 받는다. 이 코드에서는 중단 후 `finally`에서 정리하도록 의도한다.

### 6.6 70~73행 — 자원 정리

```python
finally:
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
```

- `finally`: 정상 종료와 예외 종료 경로에서 정리 작업을 수행하도록 하는 Python 구문.
- `destroy_node()`: 생성한 ROS2 노드와 관련 리소스를 정리한다.
- `rclpy.ok()`: ROS2 컨텍스트가 여전히 활성 상태인지 확인한다.
- `rclpy.shutdown()`: 활성 컨텍스트를 종료한다.
- `if rclpy.ok()` 조건은 이미 종료된 컨텍스트에 다시 종료를 요청하는 일을 피하려는 검사다.

**범위 주의:** 이 예제에서는 노드 생성이 성공한 뒤 `try/finally`로 진입한 경우를 설명한다. 노드 생성 자체가 실패한 경우까지 포괄하는 일반적인 예외 복구 코드는 아니다.

### 6.7 76~77행 — 직접 실행할 때만 `main()` 호출

```python
if __name__ == '__main__':
    main()
```

- `__name__`은 Python이 모듈에 제공하는 특별한 변수다.
- 파일을 `python3 parameter_turtle_controller.py`로 **직접 실행**하면 일반적으로 `__name__ == '__main__'`이 참이다.
- 다른 Python 파일이 이 모듈을 `import`했을 때는 보통 참이 아니다.
- 따라서 직접 실행 시에만 `main()`이 시작되게 한다.
- `main()` 호출은 위에서 정의한 함수 코드를 실제로 실행하는 시점이다.

---

---

## 7. Python 문법과 객체를 한 번 더 정리

| 표현 | Python 관점 | 이번 실습에서의 의미 |
|---|---|---|
| `class X(Node)` | 상속 | ROS2 Node 기능을 물려받는 사용자 클래스 |
| `def` | 함수/메서드 정의 | 실행할 동작을 이름으로 묶음 |
| `self` | 현재 인스턴스 참조 | Publisher, Timer, Node 메서드 접근 |
| `super().__init__()` | 부모 초기화 | 실제 ROS2 Node 상태 생성 |
| `self.publisher = ...` | 객체 속성 대입 | 여러 메서드에서 사용하는 Publisher 보관 |
| `linear_speed = ...` | 지역 변수 대입 | 한 번의 Timer Callback에서 사용할 값 |
| `self.validate_parameters` | 바운드 메서드 참조 | ROS2에 Callback 전달(즉시 호출 아님) |
| `self.validate_parameters()` | 메서드 호출 | 함수를 바로 실행하려는 표현. 여기서는 사용하지 않음 |
| `for ... in ...` | 반복문 | 파라미터 목록의 모든 원소 검사 |
| `if`, `not`, `in` | 조건 판단 | 이름/타입/범위 분기 |
| `0.0 < x <= 5.0` | 연쇄 비교 | 양수이며 상한 이하인지 검사 |
| `f'{parameter.name}...'` | f-string | 거부 사유에 대상 이름 삽입 |
| `return` | 함수 종료 및 반환 | `SetParametersResult`를 ROS2에 전달 |
| `try/except/finally` | 예외·종료 처리 | Ctrl+C를 다루고 Node/ROS2 정리 |
| `__name__ == '__main__'` | 직접 실행 판별 | 파일을 실행했을 때 `main()` 호출 |

### 7.1 `self.publisher`, `self.timer`와 지역 변수의 차이

`self.publisher`와 `self.timer`는 노드 객체가 살아 있는 동안 참조되는 **인스턴스 속성**이다. 반대로 `timer_callback()` 안의 `msg`, `linear_speed`, `angular_speed`는 호출 때마다 새로 만들어지는 **지역 변수**다.

이 구조 덕분에 Publisher는 **한 번 생성해 계속 사용**하고, 메시지와 값은 **매 타이머 주기마다 갱신**할 수 있다.

### 7.2 `Parameter`와 일반 Python `float`는 다르다

```python
parameter_obj = self.get_parameter('linear_speed')
value = parameter_obj.value
```

위 두 줄은 원본 코드의 **설명용 분해 표현**이다(원본에는 한 줄로 작성). `parameter_obj`는 ROS2 `Parameter` 객체이고, `value`는 해당 객체에 저장된 실제 숫자 값이다. `parameter_obj` 자체를 `msg.linear.x`에 대입하는 것과 `.value`를 대입하는 것은 다르다.

---

---

## 8. ROS2 API 요약: 인자, 반환값, 호출 시점

| API | 주요 인자 | 반환/효과 | 시점 |
|---|---|---|---|
| `rclpy.init(args=args)` | ROS2 인자 | ROS2 컨텍스트 초기화 | 시작 시 1회 |
| `Node.__init__(name)` | 노드 이름 문자열 | Node 기반 상태 초기화 | 노드 생성 시 1회 |
| `declare_parameter(name, value)` | 이름, 기본값 | Parameter 선언/설정 | 생성자에서 각 1회 |
| `create_publisher(Twist, topic, 10)` | 메시지 타입, Topic, QoS 깊이 | Publisher 객체 | 생성 시 1회 |
| `add_on_set_parameters_callback(callback)` | Callback 참조 | 변경 검사 Callback 등록 | 생성 시 1회 |
| `create_timer(0.1, callback)` | 초 단위 주기, Callback | Timer 객체 | 생성 시 1회 |
| `get_parameter(name)` | Parameter 이름 | 현재 `Parameter` 객체 | Timer Callback마다 각 1회 |
| `Twist()` | 없음 | `Twist` 메시지 객체 | Timer Callback마다 1회 |
| `publisher.publish(msg)` | `Twist` 메시지 | Topic 발행 요청 | Timer Callback마다 1회 |
| `SetParametersResult(...)` | 성공 여부/이유 | 검사 결과 객체 | Parameter 변경 요청 검증 시 |
| `rclpy.spin(node)` | Node 객체 | 콜백 작업 처리, 실행 유지 | 시작 후 계속 |
| `destroy_node()` | 없음 | Node 관련 리소스 정리 | 종료 시 |
| `rclpy.ok()` | 없음 | 컨텍스트 활성 여부 (`bool`) | 종료 시 |
| `rclpy.shutdown()` | 없음 | ROS2 컨텍스트 종료 | 종료 시(활성 상태일 때) |

### 8.1 Timer와 Executor의 관계

`create_timer()`는 '0.1초마다 실행할 작업'을 등록한다. 하지만 독립적으로 Python 코드를 강제로 실행하는 일반적인 무한 루프를 직접 작성한 것은 아니다. `rclpy.spin()`이 사용하는 Executor가 실행 가능한 콜백을 처리한다. 따라서 주기 0.1초는 **목표 주기**이지 모든 콜백이 정확히 소수점 아래 오차 없이 시작된다는 보장은 아니다.

사용자가 측정한 실제 값은 `average rate: 9.996`부터 `10.000` Hz 근처였고, 최소·최대 간격이 약 `0.099~0.101s`로 표시되었다. 즉 이번 환경에서는 목표 주기에 매우 가깝게 동작했다.

### 8.2 Parameter 설정과 Callback의 동기화

이번 실습에서 CLI의 `ros2 param set`은 파라미터 변경 결과를 응답으로 확인한다. **검증 콜백 자체가 값을 직접 쓰지 않고** 설정 처리 단계에서 허용 여부를 알려준다. 성공한 요청 이후에는 다음 Timer Callback에서 새 값을 읽을 수 있다.

원본은 두 파라미터를 CLI 명령 두 개로 **각각** 바꾼다. 따라서 두 명령 사이에 Timer가 실행되면 선속도만 바뀌고 각속도는 아직 이전 값일 수 있다. 이것은 코드 오류가 아니라 변경 요청이 두 번에 나누어 발생하기 때문이다.

### 8.3 검증 콜백이 모든 문제를 해결하는 것은 아니다

- 현재 검증 함수는 이름이 `linear_speed` 또는 `angular_speed`일 때만 사용자 정의 타입/범위 검사를 수행한다.
- 속도값을 `0.0`으로 정지시키는 명령은 **허용하지 않는다**. 이번 실습에서 `0.0`은 의도적으로 거부하도록 만든 테스트 조건이다.
- 실제 모바일 로봇 제어에서는 정지 명령, 전진/후진, 비상 정지, 속도 제한을 별도로 설계해야 한다. **실제 로봇에 이 예제를 안전 제어 없이 그대로 적용하면 안 된다.**

---

---

## 9. 실제 프로그램 실행 순서: 처음부터 끝까지

### 9.1 시작 순서

1. 터미널에서 `python3 parameter_turtle_controller.py`를 실행한다.
2. Python이 다섯 개 `import`를 처리한다.
3. `class ParameterTurtleController`와 `main()` 함수 정의를 읽는다. 이 단계에서는 아직 인스턴스가 만들어지지 않는다.
4. `if __name__ == '__main__':` 조건이 참이므로 `main()`을 호출한다.
5. `rclpy.init()`으로 ROS2를 초기화한다.
6. `ParameterTurtleController()`로 객체를 만든다.
7. `super().__init__()`을 통해 이름이 `parameter_turtle_controller`인 ROS2 노드 기반을 초기화한다.
8. 두 Parameter를 선언한다.
9. `Twist` Publisher를 생성한다.
10. Parameter 검증 Callback을 등록한다.
11. 0.1초 Timer를 생성하고 시작 로그를 남긴다.
12. `rclpy.spin(node)`에 진입해 준비된 콜백을 처리한다.

### 9.2 평상시 Timer 한 번 실행 순서

1. 약 0.1초가 지나 Timer 작업이 준비된다.
2. Executor가 `timer_callback()`을 호출한다.
3. `get_parameter()`로 그 시점의 `linear_speed`, `angular_speed`를 읽는다.
4. 새 `Twist()` 객체를 만든다.
5. `linear.x`, `angular.z` 필드를 설정한다.
6. Publisher가 `/turtle1/cmd_vel`에 메시지를 발행한다.
7. Turtlesim이 Topic 메시지를 받아 자신의 동작에 반영할 수 있다.
8. 다음 Timer 실행을 기다린다.

### 9.3 실행 중 변경 요청 순서

1. 터미널 3에서 `ros2 param set /parameter_turtle_controller linear_speed 1.0` 실행.
2. 해당 노드의 파라미터 변경 처리로 요청이 전달된다.
3. `validate_parameters()`가 요청의 이름, 타입, 값 범위를 검사한다.
4. 정상 값이면 `SetParametersResult(successful=True)` 반환.
5. 파라미터가 갱신되고 CLI에는 `Set parameter successful`이 표시된다.
6. 다음 Timer Callback에서 갱신된 값을 읽어 `Twist`에 적용한다.

거부되는 경우에는 4~6단계 대신 거부 결과가 반환되고 기존 값이 유지된다.

### 9.4 종료 순서

1. 터미널 2에서 `Ctrl+C`를 입력한다.
2. `spin()` 실행이 중단되는 종료 경로로 들어간다.
3. `finally`에서 `node.destroy_node()`로 노드를 정리한다.
4. ROS2 컨텍스트가 활성 상태라면 `rclpy.shutdown()`을 호출한다.
5. 터미널 1의 Turtlesim도 `Ctrl+C`로 별도 종료한다.

**프로세스 경계:** Turtlesim과 Controller는 별도 터미널·프로세스다. Controller를 종료하는 것만으로 Turtlesim 프로세스까지 자동으로 종료되는 것은 아니다.

---

---

## 10. 코드 내부에서 값이 변경되고 메시지로 이어지는 과정

이 프로그램에서 Parameter 변경에 직접 연관되는 코드는 네 군데다.

**① 선언 (14~15행)**

```python
self.declare_parameter('linear_speed', 2.0)
self.declare_parameter('angular_speed', 1.0)
```

생성자에서 기본값을 가진 파라미터를 등록한다. 초기값은 Python `float`이며 ROS2 Parameter 타입으로는 `DOUBLE`이다.

**② 검사 함수 등록 (25행)**

```python
self.add_on_set_parameters_callback(self.validate_parameters)
```

`self.validate_parameters`는 함수의 실행 결과가 아니라 **바운드 메서드에 대한 참조**다. 설정 요청이 오면 ROS2가 그 메서드에 변경 대상 `Parameter` 객체들의 목록을 전달한다.

**③ 변경 요청 검사 (32~48행)**

```python
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
```

위 코드는 원본 함수 내부의 두 조건문을 발췌한 것이다. `return`은 현재 함수 실행을 즉시 끝내므로, 첫 조건이 거짓일 때만 두 번째 검사를 진행한다. 요청을 허용하거나 거부한다는 **결과만 반환**하며, 여기서 `msg`를 만들거나 `publish()`를 호출하지 않는다. 또한 실제 파라미터 값을 직접 대입하지 않는다.

**④ Timer에서 최신 값 사용 (50~58행)**

```python
linear_speed = self.get_parameter('linear_speed').value
angular_speed = self.get_parameter('angular_speed').value

msg = Twist()
msg.linear.x = linear_speed
msg.angular.z = angular_speed

self.publisher.publish(msg)
```

파라미터 값이 변경되어도 기존에 발행한 `Twist` 메시지를 수정하지는 않는다. **다음 Timer Callback에서 새 `Twist` 객체를 만들면서** 변경된 값을 다시 읽어 발행한다.

| 순간 | 노드 내부의 파라미터 | 다음에 발행할 `Twist` |
|---|---|---|
| 노드 시작 | `2.0`, `1.0` | `linear.x=2.0`, `angular.z=1.0` |
| 두 CLI 변경 명령이 모두 성공한 뒤 | `1.0`, `3.0` | `linear.x=1.0`, `angular.z=3.0` |
| `linear_speed=0.0` 요청 거부 뒤 | `1.0`, `3.0` 유지 | 기존 유효값으로 발행 |

마지막 두 행은 실제 제공된 검증 로그로 확인됐다. 단, 두 파라미터를 변경하는 CLI 명령 사이에는 잠깐 한쪽 값만 변경된 상태가 생길 수 있다.

### 결과가 코드의 어느 부분을 검증하는가?

- `ros2 topic hz`가 약 **10 Hz**였다는 관찰은 `create_timer(0.1, ...)`와 `publish()`의 주기적 실행을 뒷받침한다.
- `ros2 topic echo`에서 `linear.x=1.0`, `angular.z=3.0`이 보인 것은 `get_parameter().value`와 필드 대입 코드가 실제 발행에 반영되었음을 보여준다.
- `0.0` 변경 요청이 거부되고 이전 값이 `1.0`으로 유지된 것은 `validate_parameters()`의 범위 검사와 `SetParametersResult(successful=False)` 처리를 검증한다.

이 세 관찰은 제공된 CLI 결과로 확인되지만, 화면에서 거북이의 실제 궤적 반지름을 측정한 결과는 아니다.

---
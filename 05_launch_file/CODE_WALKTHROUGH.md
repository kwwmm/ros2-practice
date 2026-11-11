# Practice 05 — Launch File 코드 분석

## 1. `launch/turtlesim_mimic.launch.py` 전체 코드

> 아래 코드는 실습 진행 중 대화에서 작성하고 실행한 것으로 안내한 버전이다. 현재 Ubuntu에 저장된 파일을 직접 읽어 대조하지는 못했다. 로컬 파일을 변경했다면 해당 파일을 기준으로 문서를 다시 맞춰야 한다.

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            namespace='turtlesim1',
            name='sim',
            parameters=[{
                'background_r': 100,
                'background_g': 150,
                'background_b': 255
            }]
        ),

        Node(
            package='turtlesim',
            executable='turtlesim_node',
            namespace='turtlesim2',
            name='sim',
            parameters=[{
                'background_r': 255,
                'background_g': 200,
                'background_b': 100
            }]
        ),

        Node(
            package='turtlesim',
            executable='mimic',
            name='mimic',
            remappings=[
                ('/input/pose', '/turtlesim1/turtle1/pose'),
                ('/output/cmd_vel', '/turtlesim2/turtle1/cmd_vel')
            ]
        )
    ])
```

## 2. Import 문부터 상세 분석

### `from launch import LaunchDescription`

- `from A import B`는 모듈 또는 패키지 `A`가 제공하는 이름 `B`를 현재 파일에서 직접 사용하도록 가져오는 Python 구문이다.
- `launch`는 ROS 2의 실행 구성 및 관리 프레임워크이다. 여기서 `LaunchDescription`은 **실행할 작업(Action)을 묶는 객체를 만드는 클래스**이다.
- `LaunchDescription([...])`처럼 호출하면 `LaunchDescription` 인스턴스가 생성된다. 이 실습에서는 세 개의 `Node` 실행 작업을 담는다.
- 여기서 `LaunchDescription`이라는 이름의 `Action`은 일반적인 ROS 2 **Action 통신(Goal/Feedback/Result)** 과 다른 개념이다. Launch 프레임워크에서 수행할 작업을 의미한다.
- 이 줄을 제거하면 아래의 `LaunchDescription` 이름을 찾지 못해 `NameError`가 발생한다(다른 경로로 가져오지 않는 한).

### `from launch_ros.actions import Node`

- `launch_ros`는 Launch 프레임워크와 ROS 2 노드 실행을 연결하는 Python 패키지다.
- `launch_ros.actions`에 들어 있는 `Node`는 **노드를 시작하도록 지시하는 Launch 작업 객체**를 구성하는 클래스다.
- 이 `Node`는 `rclpy.node.Node`와 **다르다**. 직접 노드의 Publisher/Subscription을 만드는 객체가 아니라, **외부 노드 프로세스를 실행하도록 설정**한다.
- 이 파일에는 `rclpy.init()`, `rclpy.spin()`, `create_publisher()`가 없는 이유도 같다. 실제 노드의 내부 통신은 `turtlesim_node`와 `mimic` 실행 파일 안에서 이루어진다.

### 빈 줄 2개

- Import 문과 최상위 함수 정의 사이의 빈 줄은 Python 스타일 가이드에서 일반적으로 권장하는 형식이다.
- 프로그램 동작을 바꾸지는 않는다.

## 3. `generate_launch_description()`와 `return`

```python
def generate_launch_description():
    return LaunchDescription([
        # Node(...) 3개
    ])
```

- `def`는 함수를 **정의**한다. 이 줄에서 세 노드를 곧바로 실행하지 않는다.
- `generate_launch_description`은 ROS 2의 Python Launch 파일을 로드할 때 Launch 시스템이 찾아 호출하는 관례적인 진입점 이름이다. 이름을 임의로 바꾸면 일반적인 Python Launch 파일 로딩 방식에서 인식되지 않는다.
- `()`는 이 함수가 이 코드에서 명시적 인자를 받지 않음을 뜻한다.
- `:`는 함수 본문의 시작을 표시하며 그 아래 들여쓴 줄들이 본문이다.
- `return`은 함수 호출 결과를 호출자에게 돌려주는 Python 키워드다. 이 경우 반환되는 것은 `LaunchDescription` 객체다. **`return` 자체가 메시지를 발행하거나 거북이를 제어하는 것은 아니다.**
- `LaunchDescription([ ... ])`의 바깥쪽 `(...)`는 클래스 생성자 호출에 쓰이는 괄호이고, 안쪽 `[...]`는 여러 `Node` 객체를 담는 **Python 리스트(list)** 다.
- 리스트의 항목은 쉼표(`,`)로 구분한다. 여기서는 첫 번째 Turtlesim, 두 번째 Turtlesim, Mimic 순으로 작업이 선언되어 있다.
- `Node(...)`는 선언을 만들고, Launch 서비스가 해당 선언을 처리하면서 각 프로세스를 시작한다. **목록의 순서가 노드의 준비 완료 시점이나 메시지 수신 순서를 엄격하게 보장하지는 않는다.**
- `])`는 리스트 `]`와 함수 호출 `)`를 닫는다. 닫는 괄호가 누락되면 `SyntaxError`가 발생할 수 있다.

## 4. 첫 번째 `Node(...)` — `turtlesim1`

```python
Node(
    package='turtlesim',
    executable='turtlesim_node',
    namespace='turtlesim1',
    name='sim',
    parameters=[{
        'background_r': 100,
        'background_g': 150,
        'background_b': 255
    }]
),
```

### `Node(`

- 클래스 이름 뒤에 괄호를 붙이는 것은 **객체 생성 호출**이다. 이 호출은 노드 실행에 필요한 설정을 수집한 Launch 작업 객체를 만든다.
- 아직 Turtlesim의 Python 객체를 직접 만든 것이 아니다. `turtlesim_node`는 별도의 실행 파일로 시작된다.

### `package='turtlesim',`

- `package`는 **키워드 인자(keyword argument)** 이름이고 `'turtlesim'`은 문자열(`str`) 값이다.
- Launch 시스템에 실행 파일이 어느 ROS 2 패키지에 속하는지 지정한다.
- `package='turtlesim'`과 `executable='turtlesim_node'`를 함께 사용하여 실행 대상을 결정한다.
- 따옴표 안은 패키지 이름이라는 **문자열 데이터**이지 Python 변수 이름이 아니다.

### `executable='turtlesim_node',`

- 패키지 안에서 실행할 실행 파일 이름이다. `ros2 pkg executables turtlesim`으로 설치된 실행 파일을 확인할 수 있다.
- 사용자 터미널에서 `turtlesim turtlesim_node`가 확인되었으므로 이 이름을 사용했다.
- `package`만 적으면 어떤 실행 파일을 시작할지 지정되지 않는다.

### `namespace='turtlesim1',`

- 노드가 속할 ROS 2 **네임스페이스(namespace)** 를 설정한다.
- `'turtlesim1'`은 이름 앞에 붙는 논리적 구분자다. 이 실습에서 노드 이름 `sim`과 결합하면 완전한 노드 이름은 `/turtlesim1/sim`이 된다.
- 상대 이름을 사용하는 Topic도 기본적으로 이 네임스페이스를 따라 `/turtlesim1/turtle1/pose`, `/turtlesim1/turtle1/cmd_vel`처럼 구분된다.
- 네임스페이스는 **Python 패키지의 네임스페이스**나 **운영체제 폴더 이름**과는 다르다. ROS 그래프에서 노드와 인터페이스 이름을 구분하는 규칙이다.
- 같은 `sim` 이름을 가진 두 노드를 각각 다른 네임스페이스에 놓아 이름 충돌을 방지한다.

### `name='sim',`

- 해당 노드에 부여할 ROS 노드 이름이다.
- 전체 이름은 네임스페이스와 결합되어 `/turtlesim1/sim`이 된다.
- 이 이름은 실제 Python 클래스 이름이 아니다.

### `parameters=[{ ... }]`

- `parameters`는 실행 시 해당 노드에 전달할 ROS 2 Parameter 목록이다.
- `[`와 `]`로 둘러싼 것은 **리스트**, `{`와 `}`로 둘러싼 것은 **딕셔너리(dict)** 다.
- 딕셔너리는 `'키': 값`의 쌍으로 구성된다. `'background_r'`는 문자열 키이고 `100`은 정수(`int`) 값이다.
- 리스트 안에 딕셔너리가 하나 있으므로 자료구조는 다음과 같다.

```python
[
    {
        'background_r': 100,
        'background_g': 150,
        'background_b': 255
    }
]
```

| 파라미터 | 값 | 의미 |
|---|---:|---|
| `background_r` | `100` | 빨강 채널 |
| `background_g` | `150` | 초록 채널 |
| `background_b` | `255` | 파랑 채널 |

- 세 색상 성분은 Turtlesim 배경색을 구성하며, 이 설정은 파란색 계열 배경을 만든다.
- 색상 Parameter는 실행 시 노드에 전달되며, 별도의 Topic 메시지로 보내는 것이 아니다.
- `ros2 param get /turtlesim1/sim background_b`로 실행 중 값을 조회할 수 있다.
- 마지막 `}),`의 `}`는 딕셔너리, `]`는 리스트, `)`는 `Node` 호출을 각각 닫는다. 뒤의 쉼표는 **다음 Node 객체와 리스트 항목을 구분**한다.

## 5. 두 번째 `Node(...)` — `turtlesim2`

```python
Node(
    package='turtlesim',
    executable='turtlesim_node',
    namespace='turtlesim2',
    name='sim',
    parameters=[{
        'background_r': 255,
        'background_g': 200,
        'background_b': 100
    }]
),
```

- `package`와 `executable`은 첫 번째와 같으므로 **같은 실행 프로그램의 별도 프로세스**가 시작된다.
- `namespace='turtlesim2'` 때문에 전체 노드 이름은 `/turtlesim2/sim`이 된다.
- 첫 번째와 두 번째 모두 `name='sim'`이지만 서로 다른 네임스페이스를 사용한다. 두 창을 구별하는 핵심 설정이다.
- 이번에는 RGB 값이 `(255, 200, 100)`이므로 주황색 계열 배경을 설정한다.
- 각 Turtlesim 프로세스에는 자체 `turtle1`이 존재한다. 따라서 두 거북이의 위치 상태가 자동으로 하나로 공유되지는 않는다.
- 두 번째 시뮬레이터를 움직이려면 **그 시뮬레이터의** `/turtlesim2/turtle1/cmd_vel`에 속도 메시지를 전달해야 한다.
- 네임스페이스를 삭제하면 노드 이름과 Topic 이름이 예상과 달라져 세 번째 노드의 리매핑 대상과 어긋날 수 있다. 단순히 화면 색만 바뀌는 설정이 아니다.

## 6. 세 번째 `Node(...)` — Mimic 및 Topic Remapping

```python
Node(
    package='turtlesim',
    executable='mimic',
    name='mimic',
    remappings=[
        ('/input/pose', '/turtlesim1/turtle1/pose'),
        ('/output/cmd_vel', '/turtlesim2/turtle1/cmd_vel')
    ]
)
```

### `package='turtlesim'`와 `executable='mimic'`

- 같은 `turtlesim` 패키지에서 이번에는 `mimic` 실행 파일을 선택한다.
- 실습 환경에서 `ros2 pkg executables turtlesim` 출력에 `turtlesim mimic`이 존재함을 확인했다.
- `mimic` 실행 파일의 구독/발행 동작은 해당 패키지 안에 **이미 구현되어 있다**. Launch 파일에서는 이를 직접 다시 구현하지 않는다.

### `name='mimic'`

- 이 노드에 `mimic`이라는 이름을 부여한다.
- `namespace`를 따로 지정하지 않아 이 구성에서는 `/mimic` 노드로 나타난다.
- `/mimic`은 거북이 이름이 아니라 **노드 이름**이다.

### `remappings=[ ... ]`

- `remappings`는 ROS 이름을 다른 ROS 이름으로 매핑하는 **리매핑 규칙의 리스트**다.
- 여기서는 두 개의 **튜플(tuple)** 이 들어 있다.
- 튜플은 `(값1, 값2)` 형식의 Python 자료형이다. 각 튜플의 첫 번째 원소가 기존 이름, 두 번째 원소가 연결할 새 이름이다.
- 값들은 모두 문자열이며 Topic 이름을 뜻한다. `=>` 같은 별도 Python 연산자가 아니라 **튜플 안의 두 문자열**로 매핑을 표현하는 것이다.

#### 첫 번째 리매핑

```python
('/input/pose', '/turtlesim1/turtle1/pose')
```

- Mimic 노드가 사용하는 `/input/pose`라는 입력 Topic을 `/turtlesim1/turtle1/pose`에 연결한다.
- 데이터가 흐르는 방향은 **첫 번째 Turtlesim의 Pose Publisher → Mimic의 Pose Subscriber**이다.
- `turtlesim/msg/Pose`는 거북이의 위치와 방향, 속도 관련 상태를 전달하는 메시지 타입이다. 주요 필드는 `x`, `y`, `theta`, `linear_velocity`, `angular_velocity`이다.
- Topic 앞의 `/`는 **절대 ROS 이름**을 의미한다. `turtlesim1`과 `turtlesim2`가 서로 다른 네임스페이스에 있어도 정확한 전체 Topic을 지정할 수 있다.

#### 두 번째 리매핑

```python
('/output/cmd_vel', '/turtlesim2/turtle1/cmd_vel')
```

- Mimic의 출력 Topic `/output/cmd_vel`을 두 번째 거북이의 속도 명령 Topic으로 변경한다.
- 데이터가 흐르는 방향은 **Mimic의 Twist Publisher → 두 번째 Turtlesim의 Twist Subscriber**이다.
- 속도 명령 메시지 타입은 `geometry_msgs/msg/Twist`이고, `linear`와 `angular`라는 두 개의 3차원 벡터를 가진다.
- Turtlesim의 평면 이동에서는 주로 `linear.x`와 `angular.z`를 사용한다.
- 이 설정은 **첫 번째 거북이의 `cmd_vel`을 두 번째 거북이에게 그대로 복사하는 것과 다르다.** 중간에 Mimic 노드가 첫 번째 거북이의 `pose`를 읽고 자신의 규칙으로 속도 명령을 만든다.

### `remappings`와 `parameters`의 차이

| 구분 | `parameters` | `remappings` |
|---|---|---|
| 목적 | 노드의 설정 데이터 전달 | 노드의 ROS 통신 이름 변경 |
| 이번 실습 | 배경 RGB | Pose 입력 / Twist 출력 연결 |
| 대표 자료형 | 딕셔너리를 담은 리스트 | 문자열 튜플의 리스트 |
| 효과 | 시뮬레이터의 배경색 설정 | 구독·발행 Topic을 다른 노드에 연결 |

### 왜 두 거북이가 반대 방향으로 움직일 수 있나?

실습 중 **아래 방향키를 눌렀을 때 한 거북이는 앞으로, 다른 거북이는 뒤로 움직이는 현상**을 관찰했다.

이 구성의 데이터 경로는 다음과 같다.

```text
터미널의 방향키
  → /turtlesim1/turtle1/cmd_vel (Twist)
  → 첫 번째 Turtlesim의 이동
  → /turtlesim1/turtle1/pose (Pose)
  → /mimic의 입력
  → Mimic 내부 로직
  → /turtlesim2/turtle1/cmd_vel (Twist)
  → 두 번째 Turtlesim의 이동
```

따라서 둘째 거북이에 전달되는 명령은 첫째 거북이에게 입력한 Twist 메시지의 단순 복사가 아니다. `mimic` 내부 변환 로직과 현재 Pose에 따라 속도 및 회전 방향이 다르게 보일 수 있다. 이 Launch 파일만으로는 Mimic 실행 파일의 **내부 계산식까지 직접 확인할 수 없으므로**, 내부 공식은 여기에서 임의로 단정하지 않는다. 두 실제 메시지를 각각 확인하면 현상을 분석할 수 있다.

```bash
ros2 topic echo /turtlesim1/turtle1/pose
# Ctrl+C 후
ros2 topic echo /turtlesim2/turtle1/cmd_vel
```

## 7. Launch의 실행 순서와 ROS 2 프로세스 구분

1. 터미널에서 `ros2 launch ~/ros2_practice/05_launch_file/launch/turtlesim_mimic.launch.py`를 실행한다.
2. ROS 2 Launch 시스템이 Python 파일을 로드하고 필요한 모듈을 import한다.
3. Launch 로더가 `generate_launch_description()`을 호출한다.
4. Python은 리스트 안에 선언된 `Node(...)` 표현식들을 평가하고 세 작업 객체를 만든다.
5. 함수가 `LaunchDescription` 인스턴스를 반환한다.
6. Launch 시스템이 각 작업을 실행하여 Turtlesim 두 프로세스와 Mimic 프로세스를 시작한다.
7. 각각의 실행 파일이 자신의 ROS 노드와 통신 객체를 내부에서 생성하고 관리한다.
8. 거북이를 조종하면 첫 번째 Turtlesim이 Pose를 발행하고, Mimic이 이를 받아 두 번째 거북이용 Twist를 발행한다.
9. Launch 실행 터미널을 `Ctrl+C`로 종료하면 Launch 시스템이 시작한 프로세스들을 종료하도록 처리한다.

**중요:** 이 Python 파일에는 `main()`, `rclpy.init()`, `rclpy.spin()` 또는 명시적 Callback 함수가 없다. Launch 파일의 역할은 **노드를 실행하고 연결을 설정하는 것**이며, 실제 Pose 콜백과 Twist 발행 동작은 별개인 `mimic` 프로세스 안에서 수행된다. 따라서 이 파일에 없는 Callback 코드를 만들어서 설명하면 안 된다.

### Launch 로드 시점과 통신 시점은 다르다

- Launch 파일의 함수 호출은 실행 구성을 **한 번 반환**한다.
- Pose 메시지 수신과 Twist 발행은 노드가 살아 있는 동안 **반복**된다.
- `Node(...)` 설정에는 `create_subscription()` 호출이 직접 들어 있지 않다. 하지만 그 설정으로 시작된 `mimic` 실행 파일은 자신의 Subscriber와 Publisher를 갖는다.
- Publisher/Subscriber 간 Topic 연결은 같은 프로세스 안에 있어야만 가능한 것은 아니다. ROS 2 미들웨어를 통해 별도의 프로세스 사이에서 통신한다.

## 8. 실제 동작을 확인하는 명령과 해석

> 아래는 검증 방법이며, 모든 명령의 실제 출력까지 대화에서 확인한 것은 아니다.

```bash
ros2 node list
```

예상 노드: `/turtlesim1/sim`, `/turtlesim2/sim`, `/mimic`.

```bash
ros2 node info /mimic
```

- Subscription 목록에 `/turtlesim1/turtle1/pose`가 있는지 확인한다.
- Publisher 목록에 `/turtlesim2/turtle1/cmd_vel`이 있는지 확인한다.
- ROS 노드는 `/rosout` 및 Parameter 관련 서비스도 가질 수 있으므로 Topic/서비스가 세 개만 나타나는 것은 아니다.

```bash
ros2 topic info /turtlesim1/turtle1/pose
ros2 topic info /turtlesim2/turtle1/cmd_vel
```

- `pose`의 Type이 `turtlesim/msg/Pose`인지 확인한다.
- `cmd_vel`의 Type이 `geometry_msgs/msg/Twist`인지 확인한다.

```bash
ros2 param get /turtlesim1/sim background_b
ros2 param get /turtlesim2/sim background_r
```

- 둘 다 설정상 `255`가 예상된다. 실제 출력 확인 전에는 이를 관측 결과로 적지 않는다.

### 처음 발생한 실행 오류의 원인

실습 초기에 파일이 존재하지 않는 상태에서 `ros2 launch turtlesim_mimic.launch.py`와 `ros2 launch ./turtlesim_mimic.launch.py`를 실행하여 **유효한 패키지 이름이 아니다**라는 오류를 확인했다. 이후 `ls`와 `py_compile` 출력에서 해당 경로에 Python 파일이 실제로 없다는 것이 확인됐다.

- `ros2 launch <package_name> <launch_file_name>`는 설치된 패키지의 Launch 파일을 실행하는 일반적인 형태다.
- 이번 실습은 설치된 사용자 패키지를 만들지 않았으므로 파일의 절대 경로를 직접 전달한다.

```bash
ros2 launch ~/ros2_practice/05_launch_file/launch/turtlesim_mimic.launch.py
```

- 먼저 `ls -l ~/ros2_practice/05_launch_file/launch/`로 실제 파일 존재 여부를 확인해야 한다.
- `python3 -m py_compile ~/ros2_practice/05_launch_file/launch/turtlesim_mimic.launch.py`는 **문법** 검사이지 ROS 노드 실행 성공 여부를 보장하는 검사는 아니다.

## 9. 코드 변경 실험 — 원본을 보존하면서 확인하기

다음 실험은 기존 코드를 직접 덮어쓰지 않도록 먼저 사본을 만든 뒤 진행한다.

```bash
cd ~/ros2_practice/05_launch_file/launch
cp turtlesim_mimic.launch.py turtlesim_mimic_experiment.launch.py
```

### 실험 A — 배경색 Parameter 변경

원본(실험 사본의 첫 번째 Node):

```python
'background_r': 100,
'background_g': 150,
'background_b': 255
```

변경:

```python
'background_r': 255,
'background_g': 255,
'background_b': 255
```

**예상 결과:** 첫 번째 창의 배경이 흰색 계열로 바뀐다. 검증 방법: 실험 Launch 파일을 실행하고 화면과 `ros2 param get /turtlesim1/sim background_r` 값을 확인한다.

### 실험 B — 두 번째 네임스페이스 이름 변경

원본:

```python
namespace='turtlesim2',
```

변경:

```python
namespace='robot2',
```

**예상 결과:** 두 번째 노드의 이름 및 기본 Topic 경로가 `/robot2/...`로 바뀐다. 그러나 기존 Mimic 출력 리매핑은 여전히 `/turtlesim2/turtle1/cmd_vel`이므로 **두 번째 거북이가 원하는 대로 움직이지 않을 수 있다**. 네임스페이스 변경이 실제 통신 경로에 영향을 준다는 점을 확인하는 실험이다.

정상 연결로 되돌리려면 실험 사본에서 다음 설정도 함께 바꾼다.

```python
('/output/cmd_vel', '/robot2/turtle1/cmd_vel')
```

**검증 방법:** `ros2 node list`, `ros2 node info /mimic`, `ros2 topic list`를 비교한다. 실패한 연결을 그대로 관측하려면 두 Launch를 동시에 실행하지 말고 실험용 Launch만 실행한다.

### 실험 C — Mimic Node 제외

실험 사본에서 세 번째 `Node(package='turtlesim', executable='mimic', ...)` 항목 전체를 제거하고 첫 번째 및 두 번째 Turtlesim `Node`만 유지한다. 리스트 쉼표 및 괄호의 균형에 주의한다.

**예상 결과:** 두 창은 계속 실행되지만 Mimic이 없으므로 첫 번째 거북이의 Pose가 두 번째 거북이의 Twist로 전달되지 않는다. `ros2 node list`에 `/mimic`이 없는지 확인한다.

실험을 마친 뒤에는 원본 `turtlesim_mimic.launch.py`를 계속 사용하고, 실험용 파일은 필요할 때만 유지한다.

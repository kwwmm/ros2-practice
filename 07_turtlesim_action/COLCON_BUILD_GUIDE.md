# ROS2 `colcon build` 상세 정리

> 학습 환경: Ubuntu 24.04 LTS · ROS2 Jazzy · Python 3.12  
> 예제: `~/ros2_practice/07_turtlesim_action/`의 `turtle_move_interfaces` 패키지

## 1. `colcon build`란?

`colcon`은 여러 ROS2 패키지를 찾아 빌드·테스트·설치 작업을 관리하는 도구다. `colcon build`를 실행하면 각 패키지의 빌드 시스템(CMake, Python 패키징 등)을 호출하고 의존성에 맞는 순서로 빌드한다. **Python 스크립트를 실행하는 명령은 아니다.**

```bash
colcon build --symlink-install
```

| 요소 | 의미 |
|---|---|
| `colcon` | 패키지 빌드와 테스트 등을 관리하는 도구 |
| `build` | 패키지 빌드 명령 |
| `--symlink-install` | 지원되는 파일을 복사 대신 심볼릭 링크로 설치하는 옵션 |

### 왜 실습 07에서 빌드했을까?

실습 01처럼 일반 `rclpy` Python 파일만 사용할 때는 환경을 활성화한 뒤 곧바로 실행할 수 있었다.

```bash
python3 publisher.py
python3 subscriber.py
```

하지만 실습 07에서는 직접 정의한 `MoveToGoal.action`을 다음처럼 Python에서 사용한다.

```python
from turtle_move_interfaces.action import MoveToGoal

goal = MoveToGoal.Goal()
goal.target_x = 8.0
goal.target_y = 8.0
```

`.action` 파일 자체는 Python 소스코드가 아니라 인터페이스 **정의 파일**이다. ROSIDL 생성기가 정의를 바탕으로 Python 클래스와 ROS2 타입 지원 코드를 생성해야 한다. 이 생성을 패키지 빌드 과정에서 수행한다.

```text
MoveToGoal.action (Goal / Result / Feedback 정의)
        ↓
colcon build → CMake / ROSIDL 실행
        ↓
생성된 Python 인터페이스 및 타입 지원 코드 설치
        ↓
source install/setup.bash
        ↓
from turtle_move_interfaces.action import MoveToGoal
```

## 2. 실습 07의 원본 폴더 구조

빌드 **전** 기본 구조:

```text
~/ros2_practice/07_turtlesim_action/
├── src/
│   └── turtle_move_interfaces/
│       ├── action/
│       │   └── MoveToGoal.action
│       ├── CMakeLists.txt
│       └── package.xml
├── move_server.py
└── move_client.py
```

- `src/turtle_move_interfaces/`는 ROS2 패키지다.
- `move_server.py`, `move_client.py`는 이번 실습에서 루트 폴더에 두고 `python3`로 직접 실행하는 파일이다. **현재 구성에서는 이 두 파일 자체가 `colcon`의 빌드 대상이 아니다.**
- 빌드 명령은 패키지 폴더 내부보다 **워크스페이스 루트**인 `07_turtlesim_action/`에서 실행한다.

## 3. 빌드에 사용되는 세 파일

### 3.1 `package.xml` — 패키지 메타데이터

패키지 이름, 버전, 빌드 방식 및 의존성을 정의한다. 이번 실습에서 중요한 항목은 아래와 같다.

```xml
<name>turtle_move_interfaces</name>
<buildtool_depend>ament_cmake</buildtool_depend>
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<depend>action_msgs</depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

| 항목 | 역할 |
|---|---|
| `ament_cmake` | 패키지의 CMake 기반 빌드 시스템 |
| `rosidl_default_generators` | ROS2 인터페이스 코드 생성용 도구 |
| `action_msgs` | Action 관련 공통 메시지·타입 의존성 |
| `rosidl_default_runtime` | 생성된 인터페이스 사용에 필요한 런타임 의존성 |
| `rosidl_interface_packages` | 인터페이스 패키지 그룹 선언 |

**주의:** `<?xml version="1.0"?>` 선언 앞에 빈 줄이나 공백이 있으면 XML 파싱에 실패할 수 있다.

### 3.2 `CMakeLists.txt` — 빌드 지시서

```cmake
cmake_minimum_required(VERSION 3.8)
project(turtle_move_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/MoveToGoal.action"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
```

- `project(...)`: 프로젝트 이름을 설정한다.
- `find_package(...)`: 필요한 CMake/ROS2 도구 패키지를 찾는다.
- `rosidl_generate_interfaces(...)`: `.action` 파일을 인터페이스 코드로 생성하도록 등록한다.
- `${PROJECT_NAME}`: `project(turtle_move_interfaces)`의 이름을 참조한다.
- `ament_export_dependencies(...)`: 런타임 의존성을 패키지 사용자에게 전달한다.
- `ament_package()`: ROS2 패키지로 등록하기 위한 마무리 단계다.

### 3.3 `MoveToGoal.action` — 통신 데이터 정의

```text
float32 target_x
float32 target_y
---
bool success
float32 final_x
float32 final_y
---
float32 current_x
float32 current_y
float32 distance_remaining
```

| 영역 | 필드 | 용도 |
|---|---|---|
| Goal | `target_x`, `target_y` | 목표 좌표 전달 |
| Result | `success`, `final_x`, `final_y` | 작업 결과와 마지막 위치 |
| Feedback | `current_x`, `current_y`, `distance_remaining` | 진행 중 위치와 남은 거리 |

`---` 구분자는 Goal / Result / Feedback을 구분한다. 이 파일에서 필드 이름이나 자료형을 바꾸면 인터페이스를 **다시 빌드**해야 한다.

## 4. 빌드 후 생기는 `build`, `install`, `log`

```bash
cd ~/ros2_practice/07_turtlesim_action
colcon build --symlink-install
```

예상 폴더 구조:

```text
07_turtlesim_action/
├── src/       # 작성한 ROS2 패키지 원본
├── build/     # 설정·생성 코드·중간 빌드 결과
├── install/   # 설치 결과, 환경 설정 스크립트
└── log/       # 실행 로그 및 오류 기록
```

| 폴더 | 의미 | GitHub 업로드 |
|---|---|---|
| `src/` | 직접 작성한 패키지 소스 | 보통 포함 |
| `build/` | CMake 설정과 중간 결과 | 제외 |
| `install/` | 빌드된 패키지의 설치 결과 | 제외 |
| `log/` | 빌드 및 테스트 로그 | 제외 |

`move_server.py`와 `move_client.py`처럼 실습 루트에 만든 원본 코드도 GitHub에 포함한다. `build`, `install`, `log`는 일반적으로 `.gitignore`에 추가한다.

## 5. `source install/setup.bash`가 필요한 이유

```bash
colcon build --symlink-install  # 패키지를 빌드해 설치 결과 생성
source install/setup.bash       # 현재 터미널에서 설치 결과를 사용하도록 설정
```

- `build`는 **파일을 생성/설치**하는 작업이다.
- `source`는 **현재 Bash 셸 환경변수를 변경**하는 작업이다.
- 환경을 활성화하면 ROS2 패키지 탐색 경로, Python 모듈 탐색 경로 등이 설정되어 설치된 인터페이스를 찾을 수 있다.
- 새 터미널을 열면 해당 터미널에서도 다시 `source`해야 한다.

표준 실행 예시:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/07_turtlesim_action
source install/setup.bash
python3 move_server.py
```

`ROS_DOMAIN_ID=13`은 이 프로젝트에서 사용하는 설정이며 모든 ROS2 환경의 필수값은 아니다. 여러 터미널에서 통신하려면 도메인 설정을 맞춰야 한다.

> **`setup.bash`와 `local_setup.bash`:** `setup.bash`는 빌드 시 사용한 상위(underlay) 환경을 포함한 설정을 불러오며, `local_setup.bash`는 현재 작업공간(overlay)의 환경을 기존 환경에 추가한다. 이 실습에서는 `source install/setup.bash`를 사용한다.

## 6. `--symlink-install`의 실제 의미

일반 설치는 해당 설치 대상 파일을 복사할 수 있지만, `--symlink-install`은 지원되는 파일에 대해 원본을 가리키는 **심볼릭 링크**를 사용한다.

```text
일반 설치:      원본 파일 → 복사된 설치 파일
심볼릭 링크:    설치 경로 → 원본 파일을 가리키는 링크
```

개발 중 Python 리소스 등 일부 파일을 수정할 때 편리하지만 **모든 파일이 자동으로 실시간 갱신되는 것은 아니다.** 특히 `.action`을 변경한 경우에는 코드 생성이 다시 필요하므로 재빌드해야 한다.

## 7. 어떤 수정에 다시 빌드가 필요할까?

| 수정 대상 | 다시 `colcon build`? | 이유 |
|---|---|---|
| `MoveToGoal.action` | **필요** | 인터페이스 클래스와 타입 지원 코드 재생성 |
| `CMakeLists.txt` | **필요** | 빌드 지시 변경 |
| `package.xml` | **필요** | 패키지/의존성 설정 변경 |
| `move_server.py` | **불필요** | 이번 구조에서는 Python 파일 직접 실행 |
| `move_client.py` | **불필요** | 이번 구조에서는 Python 파일 직접 실행 |

예를 들어 속도 제어 로직을 수정했다면 서버를 종료하고 `python3 move_server.py`로 다시 실행하면 된다. 반대로 `.action` 필드를 추가하거나 변경했다면 다음처럼 재빌드한다.

```bash
cd ~/ros2_practice/07_turtlesim_action
colcon build --symlink-install
source install/setup.bash
```

그 뒤 변경된 인터페이스를 사용하는 실행 중 노드들도 재시작한다.

> 위 표는 **이번 실습의 파일 배치**를 기준으로 한다. 나중에 Python 노드를 정식 `ament_python` 패키지로 설치하거나 C++ 노드를 사용하는 경우 빌드·설치·재실행 규칙은 달라질 수 있다.

## 8. 실습 07의 정확한 빌드·검증 순서

### 8.1 환경 활성화 및 루트 이동

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/07_turtlesim_action
```

### 8.2 패키지 발견 확인

```bash
colcon list
```

예상 출력 예시:

```text
turtle_move_interfaces  src/turtle_move_interfaces  (cmake)
```

`colcon list`의 `(cmake)` 표기는 이 패키지가 CMake 방식으로 인식되었다는 뜻이다.

### 8.3 빌드

```bash
colcon build --symlink-install
```

성공 시 출력 예시:

```text
Starting >>> turtle_move_interfaces
Finished <<< turtle_move_interfaces
Summary: 1 package finished
```

### 8.4 설치 결과 활성화 및 인터페이스 확인

```bash
source install/setup.bash
ros2 interface show turtle_move_interfaces/action/MoveToGoal
```

### 8.5 Python Import 확인

```bash
python3 -c "from turtle_move_interfaces.action import MoveToGoal; print('Action import successful')"
```

예상 출력:

```text
Action import successful
```

### 8.6 생성된 모듈 위치 확인

```bash
python3 -c "import turtle_move_interfaces; print(turtle_move_interfaces.__file__)"
```

패키지 설치 위치에 따른 경로를 확인할 수 있다. 위치는 시스템과 설정에 따라 다를 수 있다.

## 9. 실제로 겪었던 오류와 해결

### 오류 A: `package.xml` 파싱 실패

```text
XML or text declaration not at start of entity: line 2, column 0
```

**원인:** `<?xml version="1.0"?>`보다 앞에 빈 줄이나 다른 문자가 들어가 있었다.

**해결:** XML 선언을 파일의 맨 처음에 두고 저장한 다음 빌드한다.

```bash
cd ~/ros2_practice/07_turtlesim_action
python3 -c "import xml.etree.ElementTree as ET; ET.parse('src/turtle_move_interfaces/package.xml'); print('XML OK')"
colcon build --symlink-install
```

### 오류 B: `install/setup.bash` 없음

```text
bash: install/setup.bash: No such file or directory
```

**원인 후보:** 아직 빌드가 성공하지 않았거나, 다른 디렉터리에서 `source`했다.

**해결:** 워크스페이스 루트와 빌드 성공 여부를 확인한다.

```bash
cd ~/ros2_practice/07_turtlesim_action
pwd
colcon build --symlink-install
source install/setup.bash
```

### 오류 C: 사용자 정의 인터페이스 Import 실패

```text
ModuleNotFoundError: No module named 'turtle_move_interfaces'
```

**원인 후보:** 인터페이스가 아직 생성/설치되지 않았거나 새 터미널에서 작업공간 환경을 활성화하지 않았다.

**해결:** 빌드 상태와 `source`를 확인하고 Import를 직접 검사한다.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_practice/07_turtlesim_action
source install/setup.bash
python3 -c "from turtle_move_interfaces.action import MoveToGoal; print('Action import successful')"
```

오류가 있다고 곧바로 전체 ROS2 재설치나 작업공간 삭제를 할 필요는 없다. 먼저 오류 메시지와 해당 파일을 확인한다.

## 10. 자주 사용하는 `colcon` 명령어

| 명령어 | 용도 |
|---|---|
| `colcon list` | 현재 작업공간에서 인식한 패키지 나열 |
| `colcon build` | 패키지 빌드 |
| `colcon build --symlink-install` | 가능한 설치 파일을 심볼릭 링크로 설치하며 빌드 |
| `colcon build --packages-select turtle_move_interfaces` | 선택한 패키지만 빌드(선행 의존성은 별도 고려) |
| `colcon test` | 테스트 실행 |
| `colcon test-result --verbose` | 테스트 결과 상세 표시 |

## 11. 핵심 개념 요약

- **`src/`**: 사용자가 작성한 ROS2 패키지 원본.
- **`build/`**: 빌드 중간 파일과 생성 결과.
- **`install/`**: ROS2가 사용할 수 있도록 설치된 결과.
- **`log/`**: 빌드·테스트의 기록.
- **`colcon build`**: ROS2 패키지를 빌드하는 작업.
- **`source install/setup.bash`**: 설치된 패키지를 **현재 터미널에서 찾도록** 환경을 활성화하는 작업.
- **이번 실습에서 빌드가 필요한 직접적인 이유**: `MoveToGoal.action`을 Python에서 불러올 수 있도록 인터페이스와 타입 지원 코드를 생성하기 위해서.

> `colcon build`와 `source`는 서로 대체하는 명령어가 아니다. **빌드 → 환경 활성화 → 인터페이스 확인 → Python 실행** 순서로 이해하면 된다.

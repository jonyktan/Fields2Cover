cmake_minimum_required(VERSION 3.8)
project(coverage_path_generator)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED) # Required for Python support in CMake
find_package(rclpy REQUIRED) # Python action server will use rclpy
find_package(rosidl_default_generators REQUIRED)
find_package(action_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

# Declare action interface
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/CoveragePathAction.action"
  DEPENDENCIES action_msgs
  DEPENDENCIES geometry_msgs
  DEPENDENCIES std_msgs
  DEPENDENCIES nav_msgs
)

### DID NOT WORK ###
# # Set variable that ament_python_install_package uses to find the source (path relative to CMakeLists.txt)
# set(AMENT_PYTHON_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")

# # Install Python modules
# ament_python_install_package(${PROJECT_NAME})
### END ###

# Manual install Python package as ament_python was buggy
install(DIRECTORY src/${PROJECT_NAME}/
  DESTINATION lib/${PROJECT_NAME}/
  # Exclude common build artifacts
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.pyc" EXCLUDE
  PATTERN "*.egg-info" EXCLUDE
)

# Install Python executables (path relative to CMakeLists.txt)
install(PROGRAMS
  src/${PROJECT_NAME}/coverage_path_generator.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  # find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  # set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  # set(ament_cmake_cpplint_FOUND TRUE)
  # ament_lint_auto_find_test_dependencies()
endif()

ament_package()

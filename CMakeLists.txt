cmake_minimum_required(VERSION 3.10)
project(PygameTemplate)

find_package(PythonInterp REQUIRED)

add_custom_target(install_deps
    COMMAND ${PYTHON_EXECUTABLE} -m pip install -r ${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Installing dependencies from requirements.txt"
)

add_custom_target(run
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/main.py
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running Pygame Template"
)

add_dependencies(run install_deps)

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src")
    install(DIRECTORY src DESTINATION bin)
endif()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/main.py")
    install(FILES main.py DESTINATION bin)
endif()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/assets")
    install(DIRECTORY assets DESTINATION bin)
endif()

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

if(WIN32)
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/run_game.bat.in"
        "${CMAKE_BINARY_DIR}/run_game.bat"
        @ONLY
    )
    install(FILES "${CMAKE_BINARY_DIR}/run_game.bat" DESTINATION bin)
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/pygametemplate.cmd.in"
        "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.cmd"
        @ONLY
    )
    install(FILES "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.cmd" DESTINATION bin)
    install(
        CODE "execute_process(COMMAND cscript.exe //Nologo \"${CMAKE_CURRENT_SOURCE_DIR}/CreateShortcut.vbs\" \"${CMAKE_INSTALL_PREFIX}/bin/run_game.bat\")"
    )
elseif(APPLE)
    set(APP_NAME "${PROJECT_NAME}.app")
    set(APP_PATH "/Applications/${APP_NAME}")
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/macos/Info.plist.in"
        "${CMAKE_BINARY_DIR}/macos/Info.plist"
        @ONLY
    )
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/macos/run_game.sh.in"
        "${CMAKE_BINARY_DIR}/run_game.sh"
        @ONLY
    )
    install(
        FILES "${CMAKE_BINARY_DIR}/run_game.sh"
        DESTINATION "${APP_PATH}/Contents/MacOS"
        PERMISSIONS OWNER_EXECUTE OWNER_READ GROUP_EXECUTE GROUP_READ WORLD_EXECUTE WORLD_READ
    )
    install(
        FILES "${CMAKE_BINARY_DIR}/macos/Info.plist"
        DESTINATION "${APP_PATH}/Contents"
    )
    install(
        FILES "${CMAKE_CURRENT_SOURCE_DIR}/assets/sprites/player.png"
        DESTINATION "${APP_PATH}/Contents/Resources"
    )
    install(
        CODE "execute_process(COMMAND ln -sf ${APP_PATH}/Contents/MacOS/run_game.sh /usr/local/bin/${PROJECT_NAME})"
    )
elseif(UNIX)
    # Linux-specific commands
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/project.desktop.in"
        "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.desktop"
    )

    install(
        FILES "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.desktop"
        DESTINATION /usr/share/applications
    )

    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/run_game_linux.sh.in"
        "${CMAKE_BINARY_DIR}/run_game_linux.sh"
        @ONLY
    )
    install(
        FILES "${CMAKE_BINARY_DIR}/run_game_linux.sh"
        DESTINATION bin
        PERMISSIONS OWNER_EXECUTE OWNER_READ GROUP_EXECUTE GROUP_READ WORLD_EXECUTE WORLD_READ
    )
    install(
        CODE "execute_process(COMMAND ln -sf ${CMAKE_INSTALL_PREFIX}/bin/run_game_linux.sh /usr/local/bin/${PROJECT_NAME})"
    )
endif()

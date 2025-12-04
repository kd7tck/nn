cmake_minimum_required(VERSION 3.12)
project(TextGameTemplate)

# Use FindPython3 instead of deprecated PythonInterp
find_package(Python3 COMPONENTS Interpreter REQUIRED)

# Set PYTHON_EXECUTABLE for backward compatibility and for use in configure_file templates
set(PYTHON_EXECUTABLE ${Python3_EXECUTABLE})

# --- Configuration ---
set(MAIN_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/main.py")
set(REQUIREMENTS_FILE "${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt")

# --- Utilities ---

# Target to install dependencies
add_custom_target(install_deps
    COMMAND ${Python3_EXECUTABLE} -m pip install -r ${REQUIREMENTS_FILE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Installing dependencies from requirements.txt"
)

# Target to run unit tests
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src")
    set(TEST_DISCOVERY_DIR "src")
else()
    set(TEST_DISCOVERY_DIR ".")
endif()

add_custom_target(test
    COMMAND ${Python3_EXECUTABLE} -m unittest discover ${TEST_DISCOVERY_DIR}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running unit tests in ${TEST_DISCOVERY_DIR}"
)
# Ensure dependencies are installed before testing
add_dependencies(test install_deps)

# Target to run the game
add_custom_target(run
    COMMAND ${Python3_EXECUTABLE} ${MAIN_SCRIPT}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running ${PROJECT_NAME}"
)
add_dependencies(run install_deps)

# Target to clean build artifacts
add_custom_target(clean_all
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_BINARY_DIR}/dist"
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_BINARY_DIR}/build"
    COMMAND ${CMAKE_COMMAND} -E remove -f "${CMAKE_BINARY_DIR}/linuxdeploy"
    COMMENT "Cleaning PyInstaller dist and build directories"
)

# --- Installation ---

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src")
    install(DIRECTORY src DESTINATION share/${PROJECT_NAME})
endif()

if(EXISTS "${MAIN_SCRIPT}")
    install(FILES main.py DESTINATION share/${PROJECT_NAME})
endif()

# --- Platform Specific Builds ---

set(BUILD_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/scripts/build.py")

if(WIN32)
    # Windows Run Script
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/run_game.bat.in"
        "${CMAKE_BINARY_DIR}/run_game.bat"
        @ONLY
    )
    install(FILES "${CMAKE_BINARY_DIR}/run_game.bat" DESTINATION bin)

    # CMD Launcher
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/textgametemplate.cmd.in"
        "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.cmd"
        @ONLY
    )
    install(FILES "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.cmd" DESTINATION bin)

    # Shortcut Script
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/CreateShortcut.vbs.in"
        "${CMAKE_BINARY_DIR}/CreateShortcut.vbs"
        @ONLY
    )
    install(
        CODE "execute_process(COMMAND cscript.exe //Nologo \"${CMAKE_BINARY_DIR}/CreateShortcut.vbs\" \"${CMAKE_INSTALL_PREFIX}/bin/run_game.bat\")"
    )
    message(STATUS "To create a desktop shortcut, right-click on the Start Menu entry and select 'Send to > Desktop (create shortcut)'.")

    # Build EXE Target
    add_custom_target(build_exe
        COMMAND ${Python3_EXECUTABLE} ${BUILD_SCRIPT} exe
                --project-name "${PROJECT_NAME}"
                --build-dir "${CMAKE_BINARY_DIR}"
                --source-dir "${CMAKE_CURRENT_SOURCE_DIR}"
                --main-script "${MAIN_SCRIPT}"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Building Windows executable with PyInstaller"
    )
    add_dependencies(build_exe install_deps)

elseif(APPLE)
    set(APP_NAME "${PROJECT_NAME}.app")
    set(APP_PATH "/Applications/${APP_NAME}")

    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/macos/Info.plist.in"
        "${CMAKE_BINARY_DIR}/macos/Info.plist"
        @ONLY
    )

    # Unix Run Script (for inside .app)
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/run_unix.sh.in"
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
        CODE "execute_process(COMMAND ln -sf ${APP_PATH}/Contents/MacOS/run_game.sh /usr/local/bin/${PROJECT_NAME})"
    )
    message(STATUS "To create a desktop shortcut, open the /Applications folder and drag '${PROJECT_NAME}.app' to your desktop.")

    # Build DMG Target
    add_custom_target(build_dmg
        COMMAND ${Python3_EXECUTABLE} ${BUILD_SCRIPT} dmg
                --project-name "${PROJECT_NAME}"
                --build-dir "${CMAKE_BINARY_DIR}"
                --source-dir "${CMAKE_CURRENT_SOURCE_DIR}"
                --main-script "${MAIN_SCRIPT}"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Building macOS application bundle and DMG"
    )
    add_dependencies(build_dmg install_deps)

elseif(UNIX AND NOT APPLE)
    # Linux Desktop File
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/project.desktop.in"
        "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.desktop"
    )
    install(
        FILES "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.desktop"
        DESTINATION /usr/share/applications
    )

    # Linux Run Script
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/run_unix.sh.in"
        "${CMAKE_BINARY_DIR}/run_game_linux.sh"
        @ONLY
    )
    install(
        FILES "${CMAKE_BINARY_DIR}/run_game_linux.sh"
        DESTINATION bin
        PERMISSIONS OWNER_EXECUTE OWNER_READ GROUP_EXECUTE GROUP_READ WORLD_EXECUTE WORLD_READ
        RENAME "${PROJECT_NAME}"
    )
    message(STATUS "To create a desktop shortcut, find '${PROJECT_NAME}' in your application menu and drag it to your desktop.")

    # Build AppImage Target
    add_custom_target(build_appimage
        COMMAND ${Python3_EXECUTABLE} ${BUILD_SCRIPT} appimage
                --project-name "${PROJECT_NAME}"
                --build-dir "${CMAKE_BINARY_DIR}"
                --source-dir "${CMAKE_CURRENT_SOURCE_DIR}"
                --main-script "${MAIN_SCRIPT}"
                --desktop-file "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.desktop"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Building Linux AppImage"
    )
    add_dependencies(build_appimage install_deps)

    # Flatpak Target
    add_custom_target(build_flatpak
        COMMAND flatpak-builder build-dir ${CMAKE_CURRENT_SOURCE_DIR}/flatpak/com.textgametemplate.dev.yml --force-clean --user --install
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMENT "Building and installing Flatpak"
    )
    add_dependencies(build_flatpak install_deps)

    # Snap Target
    add_custom_target(build_snap
        COMMAND snapcraft
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Building Snap package"
    )
    add_dependencies(build_snap install_deps)
endif()

# --- Uninstall ---

configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/uninstall.cmake.in"
    "${CMAKE_BINARY_DIR}/uninstall.cmake"
    @ONLY
)

add_custom_target(uninstall
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_BINARY_DIR}/uninstall.cmake
    COMMENT "Uninstalling ${PROJECT_NAME}"
)

# --- Help ---

add_custom_target(list_custom_targets
    COMMAND ${CMAKE_COMMAND} -E echo "Available Custom Targets:"
    COMMAND ${CMAKE_COMMAND} -E echo "  run              - Run the game"
    COMMAND ${CMAKE_COMMAND} -E echo "  test             - Run unit tests"
    COMMAND ${CMAKE_COMMAND} -E echo "  install_deps     - Install Python dependencies"
    COMMAND ${CMAKE_COMMAND} -E echo "  clean_all        - Clean PyInstaller build artifacts"
    COMMAND ${CMAKE_COMMAND} -E echo "  build_exe        - Build Windows Executable [Windows only]"
    COMMAND ${CMAKE_COMMAND} -E echo "  build_dmg        - Build macOS DMG [macOS only]"
    COMMAND ${CMAKE_COMMAND} -E echo "  build_appimage   - Build Linux AppImage [Linux only]"
    COMMAND ${CMAKE_COMMAND} -E echo "  build_flatpak    - Build Flatpak [Linux only]"
    COMMAND ${CMAKE_COMMAND} -E echo "  build_snap       - Build Snap [Linux only]"
    COMMAND ${CMAKE_COMMAND} -E echo "  uninstall        - Uninstall the game"
    COMMENT "Listing custom targets"
)

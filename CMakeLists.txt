cmake_minimum_required(VERSION 3.10)
project(TextGameTemplate)

find_package(PythonInterp REQUIRED)

add_custom_target(install_deps
    COMMAND ${PYTHON_EXECUTABLE} -m pip install -r ${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Installing dependencies from requirements.txt"
)

add_custom_target(run
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/main.py
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running Text Game Template"
)

add_dependencies(run install_deps)

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src")
    install(DIRECTORY src DESTINATION bin)
endif()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/main.py")
    install(FILES main.py DESTINATION bin)
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
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/CreateShortcut.vbs.in"
        "${CMAKE_BINARY_DIR}/CreateShortcut.vbs"
        @ONLY
    )
    install(
        CODE "execute_process(COMMAND cscript.exe //Nologo \"${CMAKE_BINARY_DIR}/CreateShortcut.vbs\" \"${CMAKE_INSTALL_PREFIX}/bin/run_game.bat\")"
    )
    message(STATUS "To create a desktop shortcut, right-click on the Start Menu entry and select 'Send to > Desktop (create shortcut)'.")

    add_custom_target(build_exe
        COMMAND ${PYTHON_EXECUTABLE} -m PyInstaller --onefile --console --name ${PROJECT_NAME} --distpath "${CMAKE_BINARY_DIR}/dist" --workpath "${CMAKE_BINARY_DIR}/build" main.py
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

    add_custom_target(build_dmg
        COMMAND ${PYTHON_EXECUTABLE} -m PyInstaller --console --name ${PROJECT_NAME} --distpath "${CMAKE_BINARY_DIR}/dist" --workpath "${CMAKE_BINARY_DIR}/build" main.py
        COMMAND hdiutil create -volname "${PROJECT_NAME}" -srcfolder "${CMAKE_BINARY_DIR}/dist/${PROJECT_NAME}.app" -ov -format UDZO "${CMAKE_BINARY_DIR}/dist/${PROJECT_NAME}.dmg"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Building macOS application bundle and DMG"
    )
    add_dependencies(build_dmg install_deps)
elseif(UNIX AND NOT APPLE)
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
        "${CMAKE_CURRENT_SOURCE_DIR}/run_unix.sh.in"
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
    message(STATUS "To create a desktop shortcut, find '${PROJECT_NAME}' in your application menu and drag it to your desktop.")

    add_custom_target(build_appimage
        COMMAND ${PYTHON_EXECUTABLE} -m PyInstaller --noconfirm --name ${PROJECT_NAME} --distpath "${CMAKE_BINARY_DIR}/dist" --workpath "${CMAKE_BINARY_DIR}/build" main.py
        COMMAND curl -L -o "${CMAKE_BINARY_DIR}/linuxdeploy" "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"
        COMMAND chmod +x "${CMAKE_BINARY_DIR}/linuxdeploy"
        COMMAND "${CMAKE_BINARY_DIR}/linuxdeploy" --appdir "${CMAKE_BINARY_DIR}/dist/${PROJECT_NAME}" --output appimage --executable "${CMAKE_BINARY_DIR}/dist/${PROJECT_NAME}/${PROJECT_NAME}" --desktop-file "${CMAKE_BINARY_DIR}/${PROJECT_NAME}.desktop"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Building Linux AppImage"
    )
    add_dependencies(build_appimage install_deps)

    add_custom_target(build_flatpak
        COMMAND flatpak-builder build-dir ${CMAKE_CURRENT_SOURCE_DIR}/flatpak/com.pygametemplate.dev.yml --force-clean --user --install
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMENT "Building and installing Flatpak"
    )
    add_dependencies(build_flatpak install_deps)

    add_custom_target(build_snap
        COMMAND snapcraft
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Building Snap package"
    )
    add_dependencies(build_snap install_deps)
endif()

configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/uninstall.cmake.in"
    "${CMAKE_BINARY_DIR}/uninstall.cmake"
    @ONLY
)

add_custom_target(uninstall
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_BINARY_DIR}/uninstall.cmake
    COMMENT "Uninstalling ${PROJECT_NAME}"
)

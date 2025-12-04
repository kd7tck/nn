#!/usr/bin/env python3
import sys
import subprocess
import os
import argparse
import shutil
import platform

def install_dependencies(requirements_file):
    print(f"Installing dependencies from {requirements_file}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])

def run_pyinstaller(name, dist_path, work_path, script_path, windowed=False, icon=None, additional_args=None):
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--name", name,
        "--distpath", dist_path,
        "--workpath", work_path,
        "--clean", # Always clean cache
        script_path
    ]

    if windowed:
        cmd.append("--noconsole")
    else:
        cmd.append("--console")

    if icon and os.path.exists(icon):
        cmd.extend(["--icon", icon])

    if additional_args:
        cmd.extend(additional_args)

    # On macOS, --onefile works but sometimes directory based is better for .app.
    # But current CMake implies onefile or directory depending on target.
    # build_exe uses --onefile. build_dmg uses directory (implied by absence of --onefile) then wraps it.
    # build_appimage uses directory.

    # We should let the caller specify --onefile in additional_args if needed,
    # or add a flag.

    print(f"Running PyInstaller: {' '.join(cmd)}")
    subprocess.check_call(cmd)

def build_exe(project_name, build_dir, source_dir, main_script):
    dist_path = os.path.join(build_dir, "dist")
    work_path = os.path.join(build_dir, "build")

    # Windows EXE
    run_pyinstaller(
        name=project_name,
        dist_path=dist_path,
        work_path=work_path,
        script_path=main_script,
        additional_args=["--onefile"]
    )
    print(f"Build complete. Executable should be in {dist_path}")

def build_dmg(project_name, build_dir, source_dir, main_script):
    if platform.system() != "Darwin":
        print("Warning: Building DMG is only supported on macOS.")
        # We try anyway if the user insists, but hdiutil is mac only.
        return

    dist_path = os.path.join(build_dir, "dist")
    work_path = os.path.join(build_dir, "build")

    # macOS .app bundle
    run_pyinstaller(
        name=project_name,
        dist_path=dist_path,
        work_path=work_path,
        script_path=main_script,
        # Standard .app creation doesn't use --onefile usually
        additional_args=[]
    )

    # Create DMG
    app_path = os.path.join(dist_path, f"{project_name}.app")
    dmg_path = os.path.join(dist_path, f"{project_name}.dmg")

    if os.path.exists(dmg_path):
        os.remove(dmg_path)

    print("Creating DMG...")
    subprocess.check_call([
        "hdiutil", "create",
        "-volname", project_name,
        "-srcfolder", app_path,
        "-ov",
        "-format", "UDZO",
        dmg_path
    ])
    print(f"DMG created at {dmg_path}")

def build_appimage(project_name, build_dir, source_dir, main_script, desktop_file):
    dist_path = os.path.join(build_dir, "dist")
    work_path = os.path.join(build_dir, "build")

    # Linux Directory build
    run_pyinstaller(
        name=project_name,
        dist_path=dist_path,
        work_path=work_path,
        script_path=main_script,
        additional_args=[]
    )

    # Download linuxdeploy
    linuxdeploy_path = os.path.join(build_dir, "linuxdeploy")
    if not os.path.exists(linuxdeploy_path):
        print("Downloading linuxdeploy...")
        subprocess.check_call([
            "curl", "-L", "-o", linuxdeploy_path,
            "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"
        ])
        os.chmod(linuxdeploy_path, 0o755)

    # Build AppImage
    app_dir = os.path.join(dist_path, project_name) # PyInstaller creates a folder with the name
    executable = os.path.join(app_dir, project_name)

    print("Building AppImage...")
    env = os.environ.copy()
    # If running in some environments, we might need to set ARCH, but usually auto-detects.

    subprocess.check_call([
        linuxdeploy_path,
        "--appdir", app_dir,
        "--output", "appimage",
        "--executable", executable,
        "--desktop-file", desktop_file
    ], cwd=build_dir, env=env) # Run in build dir so output goes there (usually)

    print("AppImage build complete.")

def main():
    parser = argparse.ArgumentParser(description="Build script for TextGameTemplate")
    parser.add_argument("target", choices=["exe", "dmg", "appimage"], help="Build target")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--build-dir", required=True)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--main-script", required=True)
    parser.add_argument("--desktop-file", help="Path to .desktop file (for AppImage)")

    args = parser.parse_args()

    if args.target == "exe":
        build_exe(args.project_name, args.build_dir, args.source_dir, args.main_script)
    elif args.target == "dmg":
        build_dmg(args.project_name, args.build_dir, args.source_dir, args.main_script)
    elif args.target == "appimage":
        if not args.desktop_file:
            print("Error: --desktop-file is required for appimage target")
            sys.exit(1)
        build_appimage(args.project_name, args.build_dir, args.source_dir, args.main_script, args.desktop_file)

if __name__ == "__main__":
    main()

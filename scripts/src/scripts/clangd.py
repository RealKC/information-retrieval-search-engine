import os
import subprocess


def clangd():
    if not os.path.exists("CMakeLists.txt"):
        print("This is not a C++ extension project, nothing to do...")
        return

    project = os.path.basename(os.getcwd())

    subprocess.run(
        [
            "cmake",
            "-B",
            "build",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
            f"-DSKBUILD_PROJECT_NAME={project}",
        ]
    )

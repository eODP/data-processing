import subprocess


def lint():
    _exec("black .")
    _exec("black ../tests")
    _exec("flake8 .")
    _exec("flake8 ../tests")


def _exec(command):
    process = subprocess.Popen(command.split())
    output, error = process.communicate()


if __name__ == "__main__":
    lint()

import subprocess


def sumLines(path: str = "./"):
    sum = 0
    for x in subprocess.check_output(["ls", path]).decode("utf-8").split():
        if "__pycache__" in x or "venv" in x:
            continue
        if ".py" in x:
            sum += (
                subprocess.check_output(["cat", path + x]).decode("utf-8").count("\n")
            )
        if "." not in x:
            sum += sumLines(path=path + x + "/")

    return sum


print(sumLines())

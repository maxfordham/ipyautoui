from ipyautoui.custom.executetasks import ExecuteTasks, SelectAndExecute

from random import random
from time import sleep
import functools


def task(s):
    t = s
    sleep(t)
    return f"sleep: {s}"


def test_ExecuteTasks():
    END = 2
    tasks = {f"task-{_}": functools.partial(task, _) for _ in range(END)}
    ex = ExecuteTasks(tasks=tasks)
    ex.start()
    assert ex.results == [f"sleep: {_}" for _ in range(END)]

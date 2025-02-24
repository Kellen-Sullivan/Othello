import matplotlib.pyplot as plt
import numpy as np
import subprocess

from GameDriver import GameDriver


command = [
    "python",           # the Python interpreter
    "GameDriver.py",    # the script you want to run
    "alphabeta",        # first argument
    "alphabeta",        # second argument
    "0", "0", "0", "0",  # subsequent numeric arguments as strings
    "8", "8"
]

result = subprocess.run(command, capture_output=True, text=True)
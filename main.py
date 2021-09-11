from classes import WorkoutLog
from classes import Deque, Node
import re

workout_log = WorkoutLog('resources/Connor Welsh workout log.txt')

x = Deque(['a', 'b', 'c', 'd', 'e'])
print(x.return_first())
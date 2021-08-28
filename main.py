from classes import WorkoutLog
import classes
import re

workout_log = WorkoutLog('resources/Connor Welsh workout log.txt')
x = workout_log.get_sets_by_exercise('Deadlift w/ Belt')
y = workout_log.get_parameter_by_exercise('Deadlift w/ Belt', 'rpe')
print(x)
print(y)

def foo(list1, list2):
    for x, y in zip(list1, list2):
        counter = 0
        ret_value = []
        while counter < x:
            ret_value.append(y)
            counter += 1
    return ret_value

print(foo(x, y))

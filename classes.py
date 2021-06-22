from collections import OrderedDict
from functions import use_iterable_nums_as_index
import constants as c
import datetime
import re


class WorkoutLog:

    def __init__(self, filename):
        self.file_name = filename
        self.raw_content = None
        self.workouts = OrderedDict()
        self.athlete_name = None
        self.start_date = None
        self.end_date = None

        self.parse()

    def parse(self):
        """ Rip through the text file, find workouts and athlete name"""
        with open(self.file_name, 'r') as f:
            self.raw_content = f.readlines()

        workout_start_indices = []
        workout_names = []
        for index, line in enumerate(self.raw_content):
            if any(day in line for day in c.DOTW) and any(month in line for month in c.MONTHS):
                workout_start_indices.append(index)
            elif re.search('Title*', line):
                workout_names.append(line.split(': ')[1].strip())
            elif re.search('Workout Log:*', line):
                self.athlete_name = line.split(': ')[1].strip()
            elif re.search('Start Date:*', line):
                self.start_date = datetime.date(int(line.split(': ')[1].split('-')[0]),
                                                int(line.split(': ')[1].split('-')[1]),
                                                int(line.split(': ')[1].split('-')[2]))
            elif re.search('End Date:*', line):
                self.end_date = datetime.date(int(line.split(': ')[1].split('-')[0]),
                                              int(line.split(': ')[1].split('-')[1]),
                                              int(line.split(': ')[1].split('-')[2]))
            else:
                continue
        workout_start_indices.append((len(self.raw_content)) - 1)
        workout_end_indices = workout_start_indices[1:]
        workout_indices = list(zip(workout_start_indices, workout_end_indices))

        # TODO: @Justin there has to be a better and more pythonic way to slice a list multiple times using a list of
        #  tupled indices
        workouts_lines = []
        for tup in workout_indices:
            workouts_lines.append(use_iterable_nums_as_index(self.raw_content, tup))

        for index, line in enumerate(workouts_lines):
            self.workouts[workout_names[index]] = Workout(workout_names[index], line)

    def __repr__(self):
        return 'WorkoutLog(\'{}\')'.format(self.file_name)

    def __str__(self):
        log = [line.split('\n')[0] for line in self.raw_content]
        return '\n'.join(log)

    def __len__(self):
        return len(self.workouts)

    def __getitem__(self, workout_number):
        key_list = list(self.workouts)
        key_value = key_list[workout_number]
        return self.workouts[key_value]


class Workout:

    def __init__(self, title, raw_content):
        self.title = title
        self.raw_content = raw_content
        self.exercises = []
        self.date = None
        self.status = None
        self.type = None
        self.mesocycle = None
        self.microcycle = None
        self.day = None

        if re.search('[0-9]\.[0-9]\.', self.title):
            self.mesocycle, self.microcycle, self.day = (int(self.title.split('.')[0]), int(self.title.split('.')[1]),
                                                         self.title.split('.')[2])

        self.parse()

    def parse(self):
        """ Rip through the workout, find exercises, date, and status"""

        exercise_start_indices = []
        for index, line in enumerate(self.raw_content):
            if any(day in line for day in c.DOTW) and any(month in line for month in c.MONTHS):
                self.date = datetime.date(int(line.split(', ')[1]),
                                          int(c.MONTHS.index(line.split(' ')[1]) + 1),
                                          int(line.split(' ')[2].strip(',')))
            elif re.search('Status*', line):
                self.status = line.split(': ')[1].title()
            elif line[0].isupper() and ')' in line and ':' in line:
                exercise_start_indices.append(index)
            else:
                continue
        exercise_start_indices.append(len(self.raw_content))
        exercise_end_indices = exercise_start_indices[1:]
        exercise_indices = list(zip(exercise_start_indices, exercise_end_indices))

        exercises_lines = []
        for tup in exercise_indices:
            exercises_lines.append(use_iterable_nums_as_index(self.raw_content, tup))

        for lines in exercises_lines:
            self.exercises.append(Exercise(lines))

        if any(c.RELEVANT_DATA_IDENTIFIER in string for string in self.raw_content) is True:
            self.type = 'Workout'
        else:
            self.type = 'Form'

    def __repr__(self):
        return 'Exercise(\'{}, {}\')'.format(self.title, self.raw_content)

    def __str__(self):
        workout = [line.split('\n')[0] for line in self.raw_content]
        return '\n'.join(workout)

    def __len__(self):
        return len(self.exercises)

    def __getitem__(self, exercise_number):
        return self.exercises[exercise_number]


class Exercise:
    def __init__(self, raw_content):
        self.raw_content = raw_content
        self.name = None
        self.type = None
        self.category = None
        self.priority = None
        self.results = None
        self.set = []

        self.parse()

    def parse(self):
        """ Rip through the exercise data, find the raw data, name, and relevant set data"""

        for index, line in enumerate(self.raw_content):
            if line[0].isupper() and ')' in line and ':' in line:
                self.name = line.split(': ')[0].split(') ')[1].strip()
            elif c.RELEVANT_DATA_IDENTIFIER in line:
                self.set.append(Set(line.split('❍ ')[1]))
            elif line.startswith('   '):
                results_start = index
                results_end = len(self.raw_content)
                raw_results = self.raw_content[results_start: results_end]
                self.results = [x.strip().strip('\n').replace(c.END_WORKOUT_IDENTIFIER, '') for x in raw_results]
                while '' in self.results:
                    self.results.remove('')
            else:
                continue

        if any(c.RELEVANT_DATA_IDENTIFIER in string for string in self.raw_content) is True:
            self.type = 'Exercise'
        else:
            self.type = 'Other'

    def __repr__(self):
        return 'Exercise(\'{}\')'.format(self.raw_content)

    def __str__(self):
        exercise = [line.split('\n')[0] for line in self.raw_content]
        return '\n'.join(exercise)

    def __len__(self):
        return len(self.set)  # TODO: find out how to get total number of sets, not the number of set objects

    def __getitem__(self, set_number):
        return self.set[set_number]

class Set:

    def __init__(self, raw_content):
        self.raw_content = raw_content
        self.stripped_data = None
        self.sets = None
        self.reps = None
        self.min_reps = None
        self.max_reps = None
        self.rpe = None
        self.p1rm = None
        self.x_index = None
        self.intensity_indices = []

        self.parse()
        self.rpe_p1rm_brzycki_convert()

    def parse(self):
        """ Rip through the set data, find the raw data, # sets, # reps, RPE, and % of 1RM"""

        def average(list_of_nums: list):
            total_num = len(list_of_nums)
            total = 0
            for num in list_of_nums:
                total += float(num)
            return total / total_num

        self.stripped_data = self.raw_content.strip('\n').split(' ')

        for index, string in enumerate(self.stripped_data):
            if 'x' in string:
                self.x_index = index
            elif '@' in string or '%' in string:
                self.intensity_indices.append(index)
            else:
                continue

        for index, string in enumerate(self.stripped_data):
            if string.isnumeric() and index < self.x_index:
                self.sets = int(string)
            elif string.isnumeric() and index > self.x_index:
                self.reps = int(string)
                self.min_reps = int(string)
                self.max_reps = int(string)
            elif '-' in string and self.x_index < index < \
                    self.intensity_indices[0]:
                self.reps = float(average([rep for rep in string.split('-')]))
                self.min_reps = int(string.split('-')[0])
                self.max_reps = int(string.split('-')[1])

        if len(self.intensity_indices) == 0:
            for x in self.stripped_data:
                if ('^' or '^same' or 'weight^') in x:
                    pass  # TODO: find out how to retrieve previous sets' intensity
        elif len(self.intensity_indices) == 1:
            string = self.stripped_data[self.intensity_indices[0]]
            if '@' in string:
                self.rpe = int(string.replace('@', ''))
            elif '%' in string:
                self.p1rm = (float(string.replace('%', ''))) / 100
        elif len(self.intensity_indices) == 2:
            intensity_list = [self.stripped_data[self.intensity_indices[0]], self.stripped_data[self.intensity_indices[
                1]]]
            for x in intensity_list:
                if '@' in x:
                    self.rpe = average([x.replace('@', '') for x in intensity_list])
                    break
                elif '%' in x:
                    self.p1rm = (average([x.replace('%', '') for x in intensity_list])) / 100
                    break
        elif len(self.intensity_indices) > 2:
            raise TypeError('There cannot be more than two RPEs or %1RM targets per set.')

    def rpe_p1rm_brzycki_convert(self):
        if self.p1rm is None and self.rpe is not None and self.reps is not None:
            adjusted_reps = self.reps + (10 - self.rpe)  # adds reps from failure to actual reps to get total reps
            self.p1rm = round((1 / (36 / (37 - adjusted_reps))), 2)
        elif self.rpe is None and self.p1rm is not None and self.reps is not None:
            self.rpe = round(((36 * self.p1rm) + self.reps - 27), 2)

    def __repr__(self):
        return 'Exercise(\'{}\')'.format(self.raw_content)

    def __str__(self):
        return self.raw_content

# test commit

        # print(self.stripped_data)
        # print('Set # is: ' + str(self.sets))
        # print('X index is: ' + str(self.x_index))
        # print('Rep # is : ' + str(self.reps))
        # print('Rep min is : ' + str(self.min_reps))
        # print('Rep max is : ' + str(self.max_reps))
        # print('Intensity index is: ' + str(self.intensity_indices))
        # print('RPE is: @' + str(self.rpe))
        # print('%1RM is: ' + str(self.p1rm))
        # print('')


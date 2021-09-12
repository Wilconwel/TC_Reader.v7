from collections import OrderedDict

import exercise_categories
from functions import use_iterable_nums_as_index
import exercise_categories as ec
import constants as c
import datetime
import re

class Deque:

    def __init__(self, nodes=None):
        self.head = None
        self.tail = None
        if nodes is not None:
            for elem in nodes:
                self.append(Node(elem))


    def prepend(self, new_node):
        """ Insert a new node to the beginning of the deque"""

        new_node.next = self.head   # update the new_node's next reference to be the current head
        if self.head is None:   # if the list is empty make the new_node the head and tail
            self.head = new_node
            self.tail = new_node
        else:   # if the list is not empty then make the old head's previous reference the new_node and then update
            # the head to the new_node
            self.head.previous = new_node
            self.head = new_node

    def append(self, new_node):
        """ Insert a new node to the end of the deque"""

        new_node.previous = self.tail
        if self.tail is None:   # if the list is empty make both the head and tail the new node
            self.head = new_node
            self.tail = new_node
        else:   # if the list is not empty then make the tail reference the new tail and set the new node as the
            # new tail
            self.tail.next = new_node
            self.tail = new_node

    def insert_before(self, target_node, new_node):
        """ Insert a new node before the target node.

        Positional arguments:
        1) the node that comes after the new node
        2) the new node to be inserted
        """

        if target_node is None:
            print('The specified target node, \'{}\' does not exist.'.format(target_node))
        else:
            new_node.previous = target_node.previous
            target_node.previous = new_node
            new_node.next = target_node
            if new_node.previous is not None:
                new_node.previous.next = new_node
            if target_node == self.head:
                self.head == new_node

    def insert_after(self, target_node, new_node):
        """ Insert a new node after the target node.

        Positional arguments:
        1) the node that comes before the new node
        2) the new node to be inserted
        """

        if target_node is None:
            print('The specified target node, \'{}\' does not exist.'.format(target_node))
        else:
            target_node.next = new_node
            new_node.next = target_node.next
            new_node.previous = target_node
            if new_node.next is not None:
                new_node.next.previous = new_node
            if target_node is self.tail:
                self.tail = new_node

    def return_first(self):
        if self.head == None:
            Exception('Deque is empty.')
        else:
            return self.head.data

    def return_last(self):
        if self.tail == None:
            Exception('Deque is empty.')
        else:
            return self.tail.data

    def __getitem__(self, node_number):
        ret_nodes = [n for n in self]
        return ret_nodes[node_number]

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node
            node = node.next

    def __str__(self):
        node = self.head
        nodes = []
        while node is not None:
            nodes.append(node.data)
            node = node.next
        return " <-> ".join(nodes)


class Node:

    def __init__(self, data):
        self.data = data
        self.next = None
        self.previous = None

    def print_siblings(self):
        if self.previous is None:
            nodes = [self.data, self.next.data]
        elif self.next is None:
            nodes = [self.previous.data, self.data]
        else:
            nodes = [self.previous.data, self.data, self.next.data]
        print(nodes)

    def __str__(self):
        return self.data

class TrueCoachReader:

    def __init__(self, parent):
        self._parent = parent

    def _get_parent(self, parent_type=None):
        if isinstance(self, parent_type if parent_type is not None else WorkoutLog):
            return self
        else:
            return self._parent._get_parent(parent_type)

    def _get_children(self, children_type=None):
        if isinstance(self, children_type if children_type is not None else WorkoutLog):
            return self
        else:
            return self._get_children(children_type)    # TODO: make this function work

    def get_workout_list(self):
        """ Returns a list of workout names as strings"""

        return list(self._get_parent(WorkoutLog).workouts.keys())


class WorkoutLog(TrueCoachReader, Node):

    def __init__(self, filename):
        super().__init__(self)
        self.file_name = filename
        self.raw_content = None
        self.workouts = OrderedDict()
        self.athlete_name = None
        self.start_date = None
        self.end_date = None

        self.parse()

    def parse(self):
        """ Rip through the text file, find workouts, start and end date, and athlete name"""
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
            self.workouts[workout_names[index]] = Workout(self, workout_names[index], line)

    def __repr__(self):
        return 'WorkoutLog(\'{}\')'.format(self.file_name)

    def __str__(self):
        log = [line.split('\n')[0] for line in self.raw_content]
        return log

    def __len__(self):
        return len(self.workouts)

    def __getitem__(self, k):
        key_list = list(self.workouts)
        if isinstance(k, slice):
            keys = key_list[k.start:k.stop:k.step]
            workouts = [self.workouts.get(key) for key in keys]
            return workouts
        else:
            key = key_list[k]
            return self.workouts.get(key)  # TODO: find way to slice workout objects

    def get_sets_by_exercise(self, exercise):
        """Find the set data for every instance of the given exercise, return a list

        Positional arguments:
        1) the exercise to be searched, inputted as a string
        """

        ret_values = []
        for l_workouts in self.workouts.values():
            for l_exer in l_workouts:
                if l_exer.name == exercise:
                    for l_protocol in l_exer.protocols:
                        ret_values.append(l_protocol.sets)
        return ret_values

    def get_parameter_by_exercise(self, exercise, parameter):
        """Find the data for the given parameter for the every instance of the given exercise, return a list

        Positional arguments:
        1) the exercise to be searched, inputted as a string
        2) the data to be returned, inputted as a string (must be 'sets', 'reps', 'p1rm', 'rpe')
        """

        ret_values = []
        for l_workouts in self.workouts.values():
            for l_exer in l_workouts:
                if l_exer.name == exercise:
                    for l_protocol in l_exer.protocols:
                        ret_values.append(getattr(l_protocol, parameter))
        return ret_values

    def get_parameter_by_exercise_category(self, exercise_category, parameter):
        """Find the data for the given parameter for all exercise instances in the given exercise category, return a list

        Positional arguments:
        1) the exercise category to be searched, inputted as a string
        2) the data to be returned, inputted as a string (must be 'sets', 'reps', 'p1rm', 'rpe')
        """

        ret_values = []
        for l_workouts in self.workouts.values():
            for l_exer in l_workouts:
                if l_exer.category == exercise_category:
                    for l_protocol in l_exer.protocols:
                        ret_values.append(getattr(l_protocol, parameter))
        return ret_values


class Workout(TrueCoachReader):

    def __init__(self, parent, title, raw_content):
        super().__init__(parent)
        self.title = title
        self.raw_content = raw_content
        self.exercises = []
        self.date = None
        self.status = None
        self.type = None
        self.mesocycle = None
        self.microcycle = None
        self.day = None

        # if regex match, update mesocycle, microcycle, and day
        if re.search('[0-9]\.[0-9]\.', self.title):  # TODO: write better regex
            self.mesocycle, self.microcycle, self.day = (int(self.title.split('.')[0]), int(self.title.split('.')[
                                                                                                1]),
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
            self.exercises.append(Exercise(self, lines))

        # if exercise contains sets, the workout is an actual workout, if not, it's probably a form or questionnaire
        if any(c.RELEVANT_DATA_IDENTIFIER in string for string in self.raw_content) is True:
            self.type = 'Workout'
        else:
            self.type = 'Form'

    def __repr__(self):
        return 'Workout(\'{}, {}\')'.format(self.title, self.raw_content)

    def __str__(self):
        workout = [line.split('\n')[0] for line in self.raw_content]
        return '\n'.join(workout)

    def __len__(self):
        return len(self.exercises)

    def __getitem__(self, exercise_number):
        return self.exercises[exercise_number]


class Exercise(TrueCoachReader):

    def __init__(self, parent, raw_content):
        super().__init__(parent)
        self.raw_content = raw_content
        self.name = None
        self.type = None
        self.category = None
        self.classification = None
        self.results = None
        self.protocols = Deque()

        self.parse()

    def parse(self):
        """ Rip through the exercise data, find the raw data, name, and relevant set data"""
        counter = 0  # counter for Protocol index
        for index, line in enumerate(self.raw_content):
            if re.search('^[A-Z][1-9]?\) [^:\n]*:.*', line):
                self.name = line.split(': ')[0].split(') ')[1].strip()
            elif line.startswith(c.RELEVANT_DATA_IDENTIFIER):
                self.protocols.append(Protocol(self, counter, line.split('❍ ')[1]))
                counter += 1
            elif line.startswith('   '):
                results_start = index
                results_end = len(self.raw_content)
                raw_results = self.raw_content[results_start: results_end]
                self.results = [x.strip().strip('\n').replace(c.END_WORKOUT_IDENTIFIER, '') for x in raw_results]
                while '' in self.results:
                    self.results.remove('')
            else:
                continue

        # if there are no sets, then this 'exercise' is something else
        if not self.protocols:
            self.type = 'Other'
        else:
            self.type = 'Exercise'

        # if this is an exercise, try to find category and classification from the first line of the raw content
        if self.type == 'Exercise':  # TODO: ask Justin if this is slow as shit
            for char in self.raw_content[0]:
                try:
                    self.category = ec.exercise_categories.get(char)
                    if self.category is None:
                        continue
                    elif self.category is not None:
                        self.classification = ec.exercise_classifications.get(char)  # once category is found check
                        # its classification
                        break
                except KeyError:
                    continue

    def __repr__(self):
        return 'Exercise(\'{}\')'.format(self.raw_content)

    def __str__(self):
        exercise = [line.split('\n')[0] for line in self.raw_content]
        return '\n'.join(exercise)

    def __len__(self):
        return sum([protocol.sets for protocol in self.protocols])

    def __getitem__(self, set_number):
        return self.protocols[set_number]


class Protocol(TrueCoachReader):

    def __init__(self, parent, protocol_index, raw_content):
        super().__init__(parent)
        self.protocol_index = protocol_index  # index of Protocol within Exercise starting at 0
        self.raw_content = raw_content
        self.stripped_data = None
        self.sets = None
        self.reps = []
        self.min_reps = []
        self.max_reps = []
        self.rpe = []
        self.p1rm = []
        self.x_index = None
        self._intensity_indices = []

        self.parse()
        self._rpe_p1rm_brzycki_convert()

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
                self._intensity_indices.append(index)
            else:
                continue

        for index, string in enumerate(self.stripped_data):
            if string.isnumeric() and index < self.x_index:
                self.sets = int(string)
            elif string.isnumeric() and index > self.x_index:
                counter = 0
                while counter < self.sets:
                    self.reps.append(int(string))
                    self.min_reps.append(int(string))
                    self.max_reps.append(int(string))
                    counter += 1
            elif '-' in string and self.x_index < index < self._intensity_indices[0]:
                counter = 0
                while counter < self.sets:
                    self.reps.append(float(average([rep for rep in string.split('-')])))
                    self.min_reps.append(int(string.split('-')[0]))
                    self.max_reps.append(int(string.split('-')[1]))
                    counter += 1

        if len(self._intensity_indices) == 0:
            for x in self.stripped_data:
                if ('^' or '^same' or 'weight^') in x:
                    counter = 0
                    while counter < self.sets:
                        self.p1rm.append(self._get_previous_protocol_p1rm())  # gets previous protocols p1rm
                        counter += 1
                else:
                    continue
        elif len(self._intensity_indices) == 1:
            string = self.stripped_data[self._intensity_indices[0]]
            if '@' in string:
                counter = 0
                while counter < self.sets:
                    self.rpe.append(int(string.replace('@', '')))
                    counter += 1
            elif '%' in string:
                counter = 0
                while counter < self.sets:
                    self.p1rm.append((float(string.replace('%', ''))) / 100)
                    counter += 1
        elif len(self._intensity_indices) == 2:
            intensity_list = [self.stripped_data[self._intensity_indices[0]], self.stripped_data[
                self._intensity_indices[1]]]
            for x in intensity_list:
                if '@' in x:
                    counter = 0
                    while counter < self.sets:
                        self.rpe.append(average([x.replace('@', '') for x in intensity_list]))
                        counter += 1
                    break
                elif '%' in x:
                    counter = 0
                    while counter < self.sets:
                        self.p1rm.append((average([x.replace('%', '') for x in intensity_list])) / 100)
                        counter += 1
                    break
        elif len(self._intensity_indices) > 2:
            raise TypeError('There cannot be more than two RPEs or %1RM targets per set.')

    def _rpe_p1rm_brzycki_convert(self):
        """ Determine which data is missing (p1rm or rpe data) and calculate it based off of the present data"""

        if self.p1rm == [] and self.rpe != [] and self.reps != []:
            adjusted_reps = self.reps[0] + (10 - self.rpe[0])  # adds reps from failure to actual reps to get total reps
            counter = 0
            while counter < self.sets:
                self.p1rm.append(round((1 / (36 / (37 - adjusted_reps))), 2))
                counter += 1
        elif self.rpe == [] and self.p1rm != [] and self.reps != []:
            calculated_rpe = round(((36 * self.p1rm[0]) + self.reps[0] - 27), 2)
            counter = 0
            while counter < self.sets:
                self.rpe.append(calculated_rpe)
                counter += 1

    def _get_previous_protocol_p1rm(self):
        """ Get the p1rm value of the previous protocol object"""

        l_exer = self._get_parent(Exercise)
        for l_protocol in l_exer:
            if l_protocol.protocol_index == self.protocol_index - 1:
                return l_protocol.p1rm[0]

    def __repr__(self):
        return 'Protocol(\'{}\', \'{}\')'.format(self.protocol_index, self.raw_content)

    def __str__(self):
        return self.raw_content

    def __len__(self):
        return self.sets

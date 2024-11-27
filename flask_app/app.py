from flask import Flask, request, jsonify, render_template
from heapq import heappop, heappush
from collections import deque, defaultdict

# Define the Task class
class Task:
    def __init__(self, name, value, duration, dependencies=None, mandatory=False, fractionable=False):
        self.name = name
        self.value = value
        self.duration = duration
        self.dependencies = dependencies if dependencies else []
        self.mandatory = mandatory
        self.fractionable = fractionable

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "duration": self.duration,
            "dependencies": self.dependencies,
            "mandatory": self.mandatory,
            "fractionable": self.fractionable,
        }

# Step 1: Build a directed graph from the task list
def build_graph(tasks):
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for task in tasks:
        in_degree[task.name] = 0

    for task in tasks:
        for dependency in task.dependencies:
            graph[dependency].append(task.name)
            in_degree[task.name] += 1

    return graph, in_degree

# Step 2: Topological sort to find a valid task order considering dependencies
def topological_sort(tasks):
    graph, in_degree = build_graph(tasks)
    task_map = {task.name: task for task in tasks}
    queue = deque([task.name for task in tasks if in_degree[task.name] == 0])
    sorted_tasks = []

    while queue:
        current = queue.popleft()
        sorted_tasks.append(task_map[current])
        for dependent in graph[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # Sort the tasks to ensure mandatory tasks come first, followed by the highest value/duration ratio
    sorted_tasks.sort(key=lambda t: (-t.mandatory, -(t.value / t.duration)))
    return sorted_tasks

# Step 3: Create a max heap for prioritizing tasks by value/duration ratio
def create_max_heap(sorted_tasks, available_time):
    max_heap = []
    for task in sorted_tasks:
        # Ensure the task meets the available time condition and prerequisites are handled
        if task.duration > 0 and (task.mandatory or available_time >= task.duration):
            heappush(max_heap, (-task.mandatory, -(task.value / task.duration), task))
    return max_heap

# Step 4: Prioritize tasks using a max heap
def prioritize_tasks(max_heap, available_time):
    selected_tasks = []
    current_time = 0

    while max_heap and current_time < available_time:
        _, _, task = heappop(max_heap)  # Updated to handle extra tuple field for mandatory flag
        if current_time + task.duration <= available_time:
            selected_tasks.append(task)
            current_time += task.duration
        elif task.fractionable:
            # Handle fractionable tasks
            fraction = (available_time - current_time) / task.duration
            selected_tasks.append(Task(f"{task.name} (Partial)", task.value * fraction, available_time - current_time))
            break

    return selected_tasks


# Flask Application
app = Flask(__name__)

# Sample Task Data
task_lists = [
    [
        Task("2024 Fall class", 10, 24, ["Leetcode"], mandatory=True, fractionable=False),
        Task("Leetcode", 6, 6, [], mandatory=False, fractionable=True),
        Task("Assignments and Exams", 10, 80, ["2024 Fall class"], mandatory=True, fractionable=False),
        Task("Networking event", 7, 9, [], mandatory=False, fractionable=False),
        Task("Job Searching and Preparation", 10, 30, ["Leetcode"], mandatory=True, fractionable=False),
        Task("Shopping and Household", 10, 5, [], mandatory=False, fractionable=False),
        Task("Exercise and Outdoor Activity", 10, 20, [], mandatory=False, fractionable=False)
    ],
    [
        Task("Leetcode", 6, 48, [], mandatory=False, fractionable=True),
        Task("2024 Fall class", 7, 24, [], mandatory=False, fractionable=False),
        Task("Assignments and Exams", 7, 80, ["2024 Fall class"], mandatory=True, fractionable=False),
        Task("Job Searching and Preparation", 5, 20, [], mandatory=False, fractionable=True),
        Task("Exercise and Outdoor Activity", 5, 20, [], mandatory=False, fractionable=True),
        Task("Shopping and Household", 5, 20, [], mandatory=False, fractionable=False),
        Task("Networking event", 6, 10, [], mandatory=False, fractionable=False)
    ],
    [
        Task("Leetcode", 10, 11, [], mandatory=False, fractionable=True),
        Task("2024 Fall class", 10, 24, [], mandatory=False, fractionable=False),
        Task("Assignments and Exams", 10, 90, ["2024 Fall class"], mandatory=True, fractionable=False),
        Task("Networking event", 10, 7, [], mandatory=False, fractionable=True),
        Task("Job Searching and Preparation", 10, 30, [], mandatory=False, fractionable=True),
        Task("Exercise and Outdoor Activity", 10, 30, [], mandatory=False, fractionable=False),
        Task("Shopping and Household", 5, 15, [], mandatory=False, fractionable=False)
    ],
    [
        Task("Shopping and Household", 4, 12, [], mandatory=False, fractionable=False),
        Task("Assignments and Exams", 5, 30, ["2024 Fall class"], mandatory=False, fractionable=False),
        Task("2024 Fall class", 5, 24, [], mandatory=False, fractionable=False),
        Task("Leetcode", 3, 20, [], mandatory=False, fractionable=True),
        Task("Networking event", 3, 5, [], mandatory=False, fractionable=False),
        Task("Exercise and Outdoor Activity", 4, 50, [], mandatory=False, fractionable=False),
        Task("Job Searching and Preparation", 5, 20, [], mandatory=False, fractionable=False)
    ],
    [
        Task("Leetcode", 6, 60, [], mandatory=False, fractionable=True),
        Task("2024 Fall class", 6, 20, [], mandatory=False, fractionable=False),
        Task("Networking event", 5, 20, [], mandatory=False, fractionable=False),
        Task("Job Searching and Preparation", 7, 50, [], mandatory=False, fractionable=True),
        Task("Shopping and Household", 7, 40, [], mandatory=False, fractionable=True),
        Task("Assignments and Exams", 8, 60, [], mandatory=False, fractionable=False),
        Task("Exercise and Outdoor Activity", 5, 15, [], mandatory=False, fractionable=False)
    ],
    [
        Task("2024 Fall class", 8, 24, [], mandatory=False, fractionable=False),
        Task("Leetcode", 10, 10, ["2024 Fall class"], mandatory=True, fractionable=False),
        Task("Assignments and Exams", 10, 80, ["2024 Fall class"], mandatory=True, fractionable=False),
        Task("Networking event", 9, 30, [], mandatory=False, fractionable=False),
        Task("Job Searching and Preparation", 10, 40, [], mandatory=False, fractionable=False),
        Task("Exercise and Outdoor Activity", 10, 30, [], mandatory=False, fractionable=False),
        Task("Shopping and Household", 7, 8, [], mandatory=False, fractionable=False)
    ],
    [
        Task("2024 Fall class", 7, 24, ["Assignments and Exams"], mandatory=True, fractionable=False),
        Task("Leetcode", 7, 9, [], mandatory=False, fractionable=False),
        Task("Assignments and Exams", 6, 40, [], mandatory=False, fractionable=False),
        Task("Networking event", 8, 8, [], mandatory=False, fractionable=False),
        Task("Exercise and Outdoor Activity", 7, 15, [], mandatory=False, fractionable=True),
        Task("Job Searching and Preparation", 7, 70, [], mandatory=False, fractionable=False),
        Task("Shopping and Household", 5, 10, [], mandatory=False, fractionable=False)
    ],
    [
        Task("Leetcode", 10, 90, [], mandatory=False, fractionable=True),
        Task("Job Searching and Preparation", 10, 45, ["Leetcode"], mandatory=True, fractionable=False),
        Task("Networking event", 8, 7, [], mandatory=False, fractionable=False),
        Task("Shopping and Household", 2, 7, [], mandatory=False, fractionable=False),
        Task("2024 Fall class", 9, 45, [], mandatory=False, fractionable=False),
        Task("Exercise and Outdoor Activity", 8, 7, [], mandatory=False, fractionable=False),
        Task("Assignments and Exams", 7, 30, [], mandatory=False, fractionable=False)
    ],
    [
        Task("Leetcode", 10, 90, [], mandatory=False, fractionable=True),
        Task("Networking event", 10, 34, ["Job Searching and Preparation"], mandatory=True, fractionable=False),
        Task("Exercise and Outdoor Activity", 10, 10, ["Shopping and Household"], mandatory=True, fractionable=False),
        Task("Assignments and Exams", 10, 60, ["2024 Fall class"], mandatory=True, fractionable=False),
        Task("2024 Fall class", 10, 25, ["Exercise and Outdoor Activity"], mandatory=True, fractionable=True),
        Task("Shopping and Household", 10, 30, [], mandatory=False, fractionable=False),
        Task("Job Searching and Preparation", 8, 30, [], mandatory=False, fractionable=False)
    ],
    [
        Task("2024 Fall class", 10, 24, [], mandatory=False, fractionable=False),
        Task("Leetcode", 10, 40, [], mandatory=False, fractionable=True),
        Task("Assignments and Exams", 10, 80, ["2024 Fall class"], mandatory=True, fractionable=True),
        Task("Exercise and Outdoor Activity", 7, 30, [], mandatory=False, fractionable=True),
        Task("Networking event", 6, 15, [], mandatory=False, fractionable=False),
        Task("Job Searching and Preparation", 8, 45, [], mandatory=False, fractionable=True),
        Task("Shopping and Household", 10, 24, [], mandatory=False, fractionable=False)
    ],
    [
        Task("Assignments", 7, 90, ["2024 Fall class"], mandatory=True, fractionable=True),
        Task("Leetcode", 6, 10, [], mandatory=False, fractionable=True),
        Task("Shopping and Household", 8, 12, [], mandatory=False, fractionable=True),
        Task("2024 Fall class", 4, 30, [], mandatory=False, fractionable=True),
        Task("Exercise and Outdoor Activity", 7, 15, [], mandatory=False, fractionable=True),
        Task("Networking event", 3, 40, [], mandatory=False, fractionable=True),
        Task("Leetcode", 7, 17, [], mandatory=False, fractionable=True)
    ]
]

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/prioritize', methods=['POST'])
def prioritize():
    participant_index = int(request.form.get('participant'))  # Index of task list
    available_time = int(request.form.get('time'))  # Time input

    # Process tasks for the selected participant
    tasks = task_lists[participant_index]
    sorted_tasks = topological_sort(tasks)
    max_heap = create_max_heap(sorted_tasks, available_time)
    prioritized_tasks = prioritize_tasks(max_heap, available_time)

    # Convert to dictionary for JSON response
    result = [task.to_dict() for task in prioritized_tasks]
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

import time


void = lambda *_, **__: None


class Condition:
    def __init__(self) -> None:
        self.init = void
        self.check = void

    def on_init(self, func) -> "Condition":
        self.init = func
        return self

    def on_check(self, func) -> "Condition":
        self.check = func
        return self

    def __or__(self, other):
        return CCond.or_(self, other)

    def __and__(self, other):
        return CCond.and_(self, other)

    def __invert__(self):
        return CCond.not_(self)


class CCond:
    @staticmethod
    def always_true() -> Condition:
        return Condition().on_check(lambda: True)

    @staticmethod
    def always_false() -> Condition:
        return Condition().on_check(lambda: False)

    @staticmethod
    def not_(condition: Condition) -> Condition:
        return condition.on_check(lambda: not condition.check())

    @staticmethod
    def and_(condition_a: Condition, condition_b: Condition) -> Condition:
        return condition_a.on_check(lambda: condition_a.check() and condition_b.check())

    @staticmethod
    def or_(condition_a: Condition, condition_b: Condition) -> Condition:
        return condition_a.on_check(lambda: condition_a.check() or condition_b.check())

    @staticmethod
    def seconds_passed(delay: int) -> Condition:
        started = 0
        condition = Condition()

        @condition.on_init
        def init():
            nonlocal started
            started = time.time()

        @condition.on_check
        def check():
            nonlocal started
            return (time.time() - started) >= delay

        return condition


void_condition = Condition()


class Task:
    def __init__(self, id_: int, parent: "TaskManager"):
        self.id = id_
        self.parent = parent
        self.start_listeners = []
        self.update_listeners = []
        self.end_listeners = []
        self.condition = void_condition
        self.continuation = False

    def start(self):
        if self.continuation:
            raise ValueError("Task already has a followup method defined.")

        @self.on_start
        def start(task):
            self.parent.start_next_task()

        self.continuation = True

    def wait(self):
        if self.continuation:
            raise ValueError("Task already has a followup method defined.")

        @self.on_end
        def end(task):
            self.parent.start_next_task()

        self.continuation = True

    def on_start(self, func):
        self.start_listeners.append(func)

    def on_update(self, func):
        self.update_listeners.append(func)

    def on_end(self, func):
        self.end_listeners.append(func)

    def did_start(self):
        if not self.continuation:
            self.wait()
        self.condition.init()
        for func in self.start_listeners:
            func(self)

    def did_update(self):
        for func in self.update_listeners:
            func(self)

    def did_end(self):
        for func in self.end_listeners:
            func(self)

    def set_condition(self, condition: Condition):
        self.condition = condition


class TaskManager:
    def __init__(self):
        self.task_queue = []
        self.running_tasks = []
        self._task_id_counter = 0

    def new_task(self) -> Task:
        self._task_id_counter += 1
        task = Task(self._task_id_counter, self)
        self.task_queue.append(task)
        return task

    def unqueue_task(self, task: Task):
        self.task_queue.remove(task)

    def start_next_task(self):
        if len(self.task_queue) == 0:
            return
        task = self.task_queue.pop(0)
        self.start_task(task)

    def start_task(self, task: Task):
        self.running_tasks.append(task)
        task.did_start()

    def _end_task(self, task: Task):
        task.did_end()
        self.running_tasks.remove(task)

    def tick(self):
        for task in self.running_tasks:
            if task.condition.check():
                self._end_task(task)
                continue
            task.did_update()

    def execute(self):
        self.start_next_task()
        while len(self.running_tasks) > 0:
            self.tick()


taskmng = TaskManager()

# def wait_for_finish(task: Task):
#     wait_task = taskmng.new_task()
#     @task.on_end
#     def _():
#         taskmng.execute()


def delay(sec: int, task: Task):
    delay_task = taskmng.new_task()

    delay_task.set_condition(CCond.seconds_passed(sec))

    @delay_task.on_end
    def _(_):
        taskmng.start_task(task)

    taskmng.unqueue_task(task)
    return delay_task

def wait_for_sec(sec: int):
    delay_task = taskmng.new_task()

    delay_task.set_condition(CCond.seconds_passed(sec))

    return delay_task

def delay_print(sec, text):
    task = taskmng.new_task()

    task.set_condition(CCond.seconds_passed(sec))

    @task.on_end
    def _(_):
        print(text)

    return task


delay_print(5, "Hello World!").pass()
delay_print(3, "Bello World!").start()
delay_print(2, "2ello World!").start()
delay_print(6, "6ello World!").start()

# wait_for_sec(3)
# delay(0, delay_print(0, "Hello World!"))

taskmng.execute()


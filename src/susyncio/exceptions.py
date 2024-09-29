class TickingStoppedTask(RuntimeError):
    @staticmethod
    def get(task):
        return TickingStoppedTask(
            f"The task {task.name} was stopped but still ticking."
        )

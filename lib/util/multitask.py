#! /usr/bin/env python
# coding: utf-8

"""带初始化的多进程Pool.

原始的multiprocessing.Pool也支持初始化参数. 但是, 所有进程的初始化参数必须是
一样的. 有时候我们需要不同的进程其初始化参数也不一样, 比如我们用多GPU对训练
好的模型进行测试的时候, 我们希望不同的进程对应不同的GPU.

这里实现两个版本, 分别对应map操作和reduce操作. 每一种操作又实现了单进程和多进
程两个版本. 如果只有一个进程, 则不启动multiprocessing, 直接在当前进程中计算.

map操作实现了类版本和函数版本. reduce操作只实现了类版本.
"""

import time
import multiprocessing

import lib.util

__all__ = ("MapTaskPool", "ReduceTaskPool", "TaskPool")

################################ map operation #################################


class MapTaskProcess(multiprocessing.Process):
    """进程类, 对应map操作."""

    def __init__(self, task_class, task_args, input_queue, output_queue):
        super().__init__()
        assert hasattr(task_class, "process")
        self.task_class = task_class
        self.task_args = task_args
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run(self):
        if isinstance(self.task_args, tuple):
            task = self.task_class(*self.task_args)
        else:
            task = self.task_class(self.task_args)
        while True:
            sid, sample = self.input_queue.get()
            if sample is None: break
            if isinstance(sample, tuple):
                self.output_queue.put((sid, task.process(*sample)))
            else:
                self.output_queue.put((sid, task.process(sample)))


class ProxyMapTaskClass:
    """将函数包装成类. 对应map操作."""

    def __init__(self, taskfun, args):
        self.args = args if isinstance(args, tuple) else (args,)
        self.taskfun = taskfun

    def process(self, *sample):
        return self.taskfun(*sample, *self.args)


class MapTaskPoolSingleThread:
    """单进程TaskPool. 用于map操作."""

    def __init__(self, task_class, task_args, task_name=None):
        assert hasattr(task_class, "process")
        assert isinstance(task_args, list)
        assert len(task_args) == 1
        task_args = task_args[0]
        if isinstance(task_args, tuple):
            self.instance = task_class(*task_args)
        else:
            self.instance = task_class(task_args)
        self.task_name = task_name or task_class.__name__

    def process(self, samples):
        results = []
        if not samples: return []
        tracker = lib.util.get_progress_tracker(total=len(samples))
        head = f"Task {self.task_name} (single thread)"
        tracker.set_description(head)
        for sample in samples:
            if isinstance(sample, tuple):
                results.append(self.instance.process(*sample))
            else:
                results.append(self.instance.process(sample))
            tracker.update(1)
        tracker.close()
        return results

    def finish(self):
        # 这里对应多进程版本的接口
        pass


class MapTaskPoolMultiThread:
    """多进程TaskPool. 用于map操作."""

    def __init__(self, task_class, task_args, task_name=None):
        assert hasattr(task_class, "process")
        assert isinstance(task_args, list)
        assert len(task_args) > 1
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()

        self.processes = []
        for args in task_args:
            process = MapTaskProcess(
                task_class,
                args,
                self.input_queue,
                self.output_queue,
            )
            self.processes.append(process)
            process.start()
        self.task_name = task_name or task_class.__name__

    def process(self, samples):
        assert self.input_queue.empty()
        assert self.output_queue.empty()
        if not samples: return []

        # 这里加上样本序号, 因为要对结果排序
        for sid, sample in enumerate(samples):
            self.input_queue.put((sid, sample))

        results = []
        num_threads = len(self.processes)
        tracker = lib.util.get_progress_tracker(total=len(samples))
        head = f"Task {self.task_name} (thread {num_threads})"
        tracker.set_description(head)
        while len(results) < len(samples):
            if self.output_queue.empty(): time.sleep(1)
            while not self.output_queue.empty():
                results.append(self.output_queue.get())
                tracker.update(1)
        tracker.close()

        results.sort(key=lambda x: x[0])
        results = list(list(zip(*results))[1])
        return results

    def finish(self):
        assert self.input_queue.empty()
        assert self.output_queue.empty()

        # 传递None让子进程退出
        for proc in self.processes:
            self.input_queue.put((None, None))
        while not self.input_queue.empty():
            time.sleep(0.1)
        # 必须保证子进程中的queue都为空, 否则会造成死锁
        for proc in self.processes:
            proc.join()


class MapTaskPool:
    """用于map操作的TaskPool入口."""

    def __init__(self, task_class, task_args, task_name=None):
        assert hasattr(task_class, "process")
        assert isinstance(task_args, list)
        if len(task_args) == 1:
            self.task_pool = MapTaskPoolSingleThread(
                task_class, task_args, task_name)  # yapf: disable
        elif len(task_args) > 1:
            self.task_pool = MapTaskPoolMultiThread(
                task_class, task_args, task_name)  # yapf: disable

    def process(self, samples):
        return self.task_pool.process(samples)

    def finish(self):
        self.task_pool.finish()

    @staticmethod
    def get_pool(num_threads, task_class_or_fun, args=tuple(), task_name=None):
        """函数版本的multiprocessing.Pool.

        task_class_or_fun (class or function):
            若为函数, 只能为全局函数或者类中的staticmethod, 函数定义如下:
            taskfun(sample, args), 如果sample或者args为tuple, 则将其展开:
            taskfun(*sample, *args).
            若为类, 则其必须包含一个成员函数: process(self, sample). 这时,
            args为类的初始化参数. 若args为tuple, 则将其展开.
        """

        # `task_class_or_fun`是一个class.
        # 这里隐含了, 每一个class实例的初始化参数一致
        task_name = task_name or task_class_or_fun.__name__
        if hasattr(task_class_or_fun, "process"):
            task_args = [args] * len(num_threads)
            return MapTaskPool(task_class_or_fun, task_args, task_name)
        # `task_class_or_fun`是一个function
        task_args = [(task_class_or_fun, args)] * num_threads
        return MapTaskPool(ProxyMapTaskClass, task_args, task_name)

    @staticmethod
    def map(num_threads, task_class_or_fun, samples, args=tuple(),
            task_name=None):  # yapf:disable
        """函数版本的map. 参数请参考get_pool."""

        task_name = task_name or task_class_or_fun.__name__
        pool = MapTaskPool.get_pool(  # yapf: disable
            num_threads, task_class_or_fun, args, task_name)
        results = pool.process(samples)
        pool.finish()
        return results


############################### reduce operation ###############################


class ReduceTaskProcess(multiprocessing.Process):
    """进程类, 对应reduce操作."""

    def __init__(self, task_class, task_args, input_queue, output_queue):
        super().__init__()
        assert hasattr(task_class, "accumulate")
        assert hasattr(task_class, "get_result")
        self.task_class = task_class
        self.task_args = task_args
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run(self):
        if isinstance(self.task_args, tuple):
            task = self.task_class(*self.task_args)
        else:
            task = self.task_class(self.task_args)

        while True:
            sample = self.input_queue.get()
            if sample is None:
                self.output_queue.put(task.get_result())
                break
            if isinstance(sample, tuple):
                task.accumulate(*sample)
            else:
                task.accumulate(sample)


class ReduceTaskPoolSingleThread:
    """单进程TaskPool. 用于reduce操作."""

    def __init__(self, task_class, task_args, task_name=None):
        assert hasattr(task_class, "accumulate")
        assert hasattr(task_class, "get_result")
        assert isinstance(task_args, list)
        assert len(task_args) == 1
        task_args = task_args[0]
        if isinstance(task_args, tuple):
            self.instance = task_class(*task_args)
        else:
            self.instance = task_class(task_args)
        self.task_name = task_name or task_class.__name__

    def accumulate(self, samples):
        tracker = lib.util.get_progress_tracker(total=len(samples))
        head = "Task ${self.task_name} (single thread)"
        tracker.set_description(head)
        for sample in samples:
            if isinstance(sample, tuple):
                self.instance.accumulate(*sample)
            else:
                self.instance.accumulate(sample)
            tracker.update(1)
        tracker.close()

    def get_result(self):
        # 这里结果是一个list, 和多进程版本保持一致
        return [self.instance.get_result()]


class ReduceTaskPoolMultiThread:
    """多进程TaskPool. 用于reduce操作."""

    def __init__(self, task_class, task_args, task_name=None):
        assert hasattr(task_class, "accumulate")
        assert hasattr(task_class, "get_result")
        assert isinstance(task_args, list)
        assert len(task_args) > 1
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()

        self.processes = []
        for args in task_args:
            process = ReduceTaskProcess(
                task_class,
                args,
                self.input_queue,
                self.output_queue,
            )
            self.processes.append(process)
            process.start()
        self.task_name = task_name or task_class().__name__

    def accumulate(self, samples):
        assert self.input_queue.empty()
        for sample in samples:
            self.input_queue.put(sample)

        num_threads = len(self.processes)
        tracker = lib.util.get_progress_tracker(total=len(samples))
        head = f"Task {self.task_name} (thread {num_threads})"
        tracker.set_description(head)
        while not self.input_queue.empty():
            processed = len(samples) - self.input_queue.qsize()
            tracker.update(processed - tracker.n)
            time.sleep(1)
        tracker.close()

    def get_result(self):
        assert self.input_queue.empty()

        # 传递None让子进程退出
        for proc in self.processes:
            self.input_queue.put(None)
        while not self.input_queue.empty():
            time.sleep(1)
        results = [self.output_queue.get() for p in self.processes]
        # 必须保证子进程中的queue都为空, 否则会造成死锁
        for proc in self.processes:
            proc.join()
        return results


class ReduceTaskPool:
    """用于reduce操作的TaskPool入口."""

    def __init__(self, task_class, task_args, task_name=None):
        assert hasattr(task_class, "accumulate")
        assert hasattr(task_class, "get_result")
        assert isinstance(task_args, list)
        if len(task_args) == 1:
            self.task_pool = ReduceTaskPoolSingleThread(
                task_class, task_args, task_name)  # yapf: diable
        elif len(task_args) > 1:
            self.task_pool = ReduceTaskPoolMultiThread(
                task_class, task_args, task_name)  # yapf disable

    def accumulate(self, samples):
        self.task_pool.accumulate(samples)

    def get_result(self):
        return self.task_pool.get_result()

    @staticmethod
    def reduce(num_threads, task_class, samples, task_args=tuple(),
               task_name=None):  # yapf: disable
        # 和map版本不同的是, reduce版本只支持class方式.
        task_args = [task_args] * num_threads
        task_name = task_name or task_class.__name__
        pool = ReduceTaskPool(task_class, task_args, task_name)
        pool.accumulate(samples)
        return pool.get_result()


# 兼容原来版本
TaskPool = MapTaskPool

if __name__ == "__main__":
    pass

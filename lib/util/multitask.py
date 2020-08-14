#! /home/chenli/Documents/tools/anaconda3/envs/pytorch/bin/python
# coding: utf-8

import time
import logging
import multiprocessing

#################### multiprocessing with initialization #######################

class TaskProcess(multiprocessing.Process):
    def __init__(self, task_class, task_args, input_queue, output_queue):
        super().__init__()
        self.task_class = task_class
        self.task_args = task_args
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run(self):
        task = self.task_class(*self.task_args)
        while True:
            sid, sample = self.input_queue.get()
            if sample is None: break
            if isinstance(sample, tuple):
                self.output_queue.put((sid, task.process(*sample)))
            else:
                self.output_queue.put((sid, task.process(sample)))


class TaskPool:
    """带初始化的多进程Pool.

    原始的multiprocessing.Pool也支持初始化参数, 但是, 所有进程的初始化参数
    必须是一样的. 有时候我们需要不同的进程其初始化参数也不一样, 比如我们用
    多GPU对训练好的模型进行测试的时候, 我们希望不同的进程对应不同的GPU.
    这个类弥补了原生Pool类的不足.

    Args:
        task_class: 每一个进程开始时初始化的类名, 其必须有一个定义如下的
            成员函数: process(self, sample).
        task_args: 一个args列表, 用来初始化task_class. 每一项对应一个进程.
    """

    def __init__(self, task_class, task_args):
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()

        self.processes = []
        for pid, args in enumerate(task_args):
            self.processes.append(TaskProcess(
                task_class, args,
                self.input_queue,
                self.output_queue))
            self.processes[-1].start()

    def process(self, samples, batch_size=0):
        """多进程批量处理函数, 类似于pool.map.

        如果samples个数太多, 一次性装入input_queue可能会导致内存不足.
        所以这里采用batch的方式: 当input_queue的大小小于batch_size的时候,
        就往里面装batch_size个样本. 不直接使用queue的阻塞机制是为了实时
        打印进度.
        """

        samples = list(enumerate(samples))
        batch_size = batch_size or len(samples)
        num_samples = len(samples)

        results = []
        while len(results) < num_samples:
            if self.input_queue.qsize() < batch_size and len(samples) != 0:
                batch_samples = samples[:batch_size]
                samples = samples[batch_size:]
                for sample in batch_samples:
                    self.input_queue.put(sample)
            while not self.output_queue.empty():
                results.append(self.output_queue.get())
            logging.info("Progress %d/%d", len(results), num_samples)
            time.sleep(5)

        results.sort(key=lambda x: x[0])
        results = list(list(zip(*results))[1])
        return results

    def finish(self):
        assert self.output_queue.empty(), \
            "Internal error: output queue must be empty."

        ### 传递None让子进程退出
        for proc in self.processes:
            self.input_queue.put((None, None))
        while not self.input_queue.empty():
            time.sleep(1)

        ### 必须保证子进程中的queue都为空, 否则会造成死锁
        for proc in self.processes:
            proc.join()

    @staticmethod
    def map(numthreads, taskfun, samples, args=None, batch_size=0):
        """函数版本的process.

        taskfun (function): 只能为全局函数或者类中的staticmethod, 函数定义
            如下: taskfun(sample, args), 如果sample或者args为tuple, 则将其
            展开: taskfun(*sample, *args).
        """

        # pylint: disable=too-few-public-methods
        class _ProxyTaskClass:
            def __init__(self, taskfun, args):
                if args is None:
                    args = tuple()
                elif not isinstance(args, tuple):
                    args = (args,)
                self.args = args
                self.taskfun = taskfun

            def process(self, sample):
                if isinstance(sample, tuple):
                    return self.taskfun(*sample, *self.args)
                return self.taskfun(sample, *self.args)

        pool = TaskPool(_ProxyTaskClass, [(taskfun, args)] * numthreads)
        results = pool.process(samples, batch_size)
        pool.finish()
        return results


if __name__ == "__main__":
    pass

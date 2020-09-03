#! /home/chenli/Documents/tools/anaconda3/envs/pytorch/bin/python
# coding: utf-8

import logging


def add_common_argument(parser, args):
    """收集常用的command line参数, 在这里集中定义.

    Args:
        parser: argparse.ArgumentParser实例.
        args: dict. key为需要定义的参数, value为默认值.
    """

    for key, value in args.items():
        # 训练数据 & 测试数据
        if key == "train_sample_file":
            parser.add_argument(
                "--train_sample_file",
                type=str,
                default=value,
                help="path of file containing list of samples for training.",
            )
        elif key == "train_root":
            parser.add_argument(
                "--train_root",
                type=str,
                default=value,
                help="root directory of training samples.",
            )
        elif key == "test_sample_file":
            parser.add_argument(
                "--test_sample_file",
                type=str,
                default=value,
                help="path of file containing list of samples for test.",
            )
        elif key == "test_root":
            parser.add_argument(
                "--test_root",
                type=str,
                default=value,
                help="root directory of test samples.",
            )
        elif key == "sample_file":
            parser.add_argument(
                "--sample_file",
                type=str,
                default=value,
                help="path of file containing list of samples.",
            )
        elif key == "sample_root":
            parser.add_argument(
                "--sample_root",
                type=str,
                default=value,
                help="root directory of samples.",
            )
        elif key == "label_file":
            parser.add_argument(
                "--label_file",
                type=str,
                default=value,
                help="path of file containing list of class names.",
            )

        # device_id
        elif key == "dali_device_id":
            parser.add_argument(
                "--dali_device_id",
                type=int,
                default=value,
                help="device id for nvidia dali.",
            )
        elif key == "torch_device_id":
            parser.add_argument(
                "--torch_device_id",
                type=int,
                default=value,
                help="device id for pytorch.",
            )
        elif key == "device_id":
            parser.add_argument(
                "--device_id",
                type=int,
                default=value,
                help="device id.",
            )
        elif key == "gpuids":
            parser.add_argument(
                "--gpuids",
                type=str,
                default=value,
                help="specify how many instances to be created on given "
                "gpus, eg: '1,1,2' means gpu1 has two instances and gpu2 "
                "has one instance.",
            )

        ### others
        elif key == "num_classes":
            parser.add_argument(
                "--num_classes",
                type=int,
                default=value,
                help="number of classes.",
            )
        elif key == "num_epoches":
            parser.add_argument(
                "--num_epoches",
                type=int,
                default=value,
                help="number of epoches performed in the training step.",
            )
        elif key == "prefix":
            parser.add_argument(
                "--prefix",
                type=str,
                default=value,
                help="Prefix of path where the trained models are stored.",
            )
        elif key == "checkpoint":
            parser.add_argument(
                "--checkpoint",
                type=str,
                default=value,
                help="Path of model which is to be evaluated or to be "
                "finetuned.",
            )
        elif key == "batch_size":
            parser.add_argument(
                "--batch_size",
                type=int,
                default=value,
                help="batch size",
            )
        elif key == "num_threads":
            parser.add_argument(
                "--num_threads",
                type=int,
                default=value,
                help="num of threads (used in multithreading case)",
            )

        else:
            assert False, "Unknown argument: {}".format(key)


def print_all_arguments(args, printfun=logging.info):
    """输出所有的ArgumentParser返回的参数."""

    printfun("{:=^64}".format(" arguments "))
    for key, value in vars(args).items():
        printfun("{:-<32} {}".format(key + " ", value))
    printfun("=" * 64)


if __name__ == "__main__":
    pass

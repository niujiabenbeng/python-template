#! /home/chenli/Documents/tools/anaconda3/envs/pytorch/bin/python
# coding: utf-8

import cv2
import numpy as np

import PIL
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw


def convert_image_CV2PIL(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = PIL.Image.fromarray(image)
    return image


def draw_textlines(image,
                   origin,
                   textlines,
                   color,
                   thickness=2,
                   font_face=cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale=1.2):
    face = font_face
    scale = font_scale
    for text in textlines:
        size, baseline = cv2.getTextSize(text, face, scale, thickness)
        origin = (origin[0], origin[1] + size[1] + baseline)
        cv2.putText(image, text, origin, face, scale, color, thickness)
    return image


def draw_chinese_textlines(image,
                           origin,
                           textlines,
                           color,
                           size=26,
                           thickness=2):
    """采用PIL往图片上写中文."""

    pilimg = PIL.Image.fromarray(image[:, :, ::-1])
    draw = PIL.ImageDraw.Draw(pilimg)
    font = PIL.ImageFont.truetype('simsun.ttc', size)
    for n, text in enumerate(textlines):
        offset_y = n * size + thickness
        for i in range(0, thickness):
            for j in range(0, thickness):
                origin_tmp = (origin[0] + i, origin[1] + j + offset_y)
                draw.text(origin_tmp, text, font=font, fill=color[::-1])
    result = np.asarray(pilimg.getdata(), dtype=np.uint8).reshape(image.shape)
    return np.require(result[:, :, ::-1], dtype=np.uint8, requirements="C")


def stitch_images(images, width=512, height=384, fill=(0, 0, 0)):
    """将<=9个patch合为一个.

    images: 包含最多9个cv2格式的image的list.
    width:  每一幅图像占据的宽度.
    height: 每一幅图像占据的高度.
    """

    assert len(images) <= 9
    if len(images) <= 1:
        rows, cols = 1, 1
    elif len(images) <= 2:
        rows, cols = 1, 2
    elif len(images) <= 4:
        rows, cols = 2, 2
    elif len(images) <= 6:
        rows, cols = 2, 3
    elif len(images) <= 9:
        rows, cols = 3, 3

    stitched = np.zeros((height * rows, width * cols, 3), dtype=np.uint8)
    stitched[:, :] = fill
    for i, image in enumerate(images):
        if image is None: continue

        # 有需要的话进行保长宽比的resize
        old_height, old_width = image.shape[:2]
        if old_height > height or old_width > width:
            new_height = height
            new_width = new_height * old_width // old_height
            if new_width > width:
                new_width = width
                new_height = new_width * old_height // old_width
            image = cv2.resize(image, (new_width, new_height))

        new_height, new_width = image.shape[:2]
        start_x = (i % cols) * width + (width - new_width) // 2
        start_y = (i // cols) * height + (height - new_height) // 2
        end_x = start_x + new_width
        end_y = start_y + new_height
        stitched[start_y:end_y, start_x:end_x, :] = image
    return stitched


def get_label_color_map(labels):
    """给每一个label生成一个color.

    方法来自: http://blog.csdn.net/yhl_leo/article/details/52185581
    """

    assert len(labels) < 256, \
        "this method can only generate 255 different colors."
    colors = []
    for i in range(len(labels)):
        r, g, b, ii = (0, 0, 0, i)
        for j in range(7):
            str_ii = "{:0>8}".format(bin(ii)[2:])[-8:]
            r = r ^ (int(str_ii[-1]) << (7 - j))
            g = g ^ (int(str_ii[-2]) << (7 - j))
            b = b ^ (int(str_ii[-3]) << (7 - j))
            ii = ii >> 3
        colors.append((r, g, b))
    return dict(zip(labels, colors))


if __name__ == "__main__":
    pass

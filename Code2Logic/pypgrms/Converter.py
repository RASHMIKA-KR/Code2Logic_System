'''
A program that converts pseudocode to .png flowcharts
'''

import re
import os
from math import log, floor

import click
from PIL import Image, ImageDraw, ImageFont

from package.tree import newTree, newNode


def read(file_name):

    script_dir = os.path.dirname(os.path.realpath(__file__))
    text_path = os.path.join(script_dir, '..', 'pseudo', file_name)
    with open(text_path, "r") as text_file:
        lines = text_file.readlines()


    processed_lines = []

    for_re = re.compile(r'^FOR\s(.+)\s<-\s(.+)\sTO\s(.+)')
    next_re = re.compile(r'^NEXT\s(.+)')

    processed_lines.append("START")

    for line in lines:

        line = line.rstrip().lstrip()

        if re.search(for_re, line):
            var = re.search(for_re, line).group(1)
            low = re.search(for_re, line).group(2)
            high = re.search(for_re, line).group(3)

            processed_lines.append(var + " = " + low)
            processed_lines.append("WHILE " + var + " < " + high + " DO")

        elif re.search(next_re, line):
            var = re.search(next_re, line).group(1)

            processed_lines.append(var + " = " + var + " + 1")
            processed_lines.append("ENDWHILE")

        elif line == '':
            pass

        else:
            processed_lines.append(line)

    processed_lines.append("STOP")

    return processed_lines


def translation(lines, font_data):

    input_re = re.compile(r'^INPUT\s(.+)')
    output_re = re.compile(r'^OUTPUT\s(.+)')

    if_re = re.compile(r'^IF\s(.+)\sTHEN$')
    else_re = re.compile(r'^ELSE$')
    endif_re = re.compile(r'^ENDIF$')

    while_re = re.compile(r'^WHILE\s(.+)\sDO$')
    endwhile_re = re.compile(r'^ENDWHILE$')

    chart_code = []

    amount_per_branch = {}
    beginning_of_split = {}

    branch_width = {}
    layer_height = {}

    font_path = font_data['path']
    font_size = font_data['size']
    font = ImageFont.truetype(font_path, font_size)

    img = Image.new('RGB', (10, 10), color='white')
    draw = ImageDraw.Draw(img)

    x = [1]
    y = [1]

    for i in range(0, len(lines)):
        line = lines[i]

        if x[-1] not in amount_per_branch:
            amount_per_branch[x[-1]] = 0
            beginning_of_split[x[-1]] = 0
            branch_width[x[-1]] = 0

        if y[-1] not in layer_height:
            layer_height[y[-1]] = draw.textsize("a", font=font)[1] + font_size

        if line == "START" or line == "STOP":

            if line == "STOP":
                chart_code.append({
                    "type": "Terminator",
                    "content": line,
                    "position": [x[-1], y[-1]],
                    "role": 't'
                })
            else:
                chart_code.append({
                    "type": "Terminator",
                    "content": line,
                    "position": [x[-1], y[-1]],
                    "role": 'n'
                })

            if draw.textsize(
                    line, font=font)[0] + font_size * 2 > branch_width[x[-1]]:
                branch_width[x[-1]] = draw.textsize(
                    line, font=font)[0] + font_size * 2

            if draw.textsize(
                    line,
                    font=font)[1] + font_size + 2 * font_size > layer_height[
                        y[-1]]:
                layer_height[y[-1]] = draw.textsize(
                    line, font=font)[1] + 2 * font_size

            amount_per_branch[x[-1]] += 1
            y[-1] += 1

        elif re.search(input_re, line) or re.search(output_re, line):
            chart_code.append({
                "type": "IO",
                "content": line,
                "position": [x[-1], y[-1]],
                "role": 'n'
            })

            if draw.textsize(
                    line, font=font)[0] + font_size * 2 > branch_width[x[-1]]:
                branch_width[x[-1]] = draw.textsize(
                    line, font=font)[0] + font_size * 2

            if draw.textsize(line,
                             font=font)[1] + font_size > layer_height[y[-1]]:
                layer_height[y[-1]] = draw.textsize(line,
                                                    font=font)[1] + font_size

            amount_per_branch[x[-1]] += 1
            y[-1] += 1

        elif re.search(if_re, line):
            chart_code.append({
                "type": "Decision",
                "content": re.search(if_re, line).group(1),
                "position": [x[-1], y[-1]],
                "role": 'o'
            })

            if len(line) > len("IF") + 1:
                width = 3 / 2 * draw.textsize(line, font=font)[0]
                height = 5 * draw.textsize(line, font=font)[1]
            else:
                width = 5 * font_size
                height = 5 * font_size

            if width > branch_width[x[-1]]:
                branch_width[x[-1]] = width

            if height > layer_height[y[-1]]:
                layer_height[y[-1]] = height

            amount_per_branch[x[-1]] += 1

            beginning_of_split[x[-1]] = y[-1]

            x.append(2 * x[-1])
            y.append(y[-1] + 1)

        elif re.search(else_re, line):
            if x[-1] % 2 == 0:
                x[-1] += 1
                y[-1] = y[-2] + 1
            else:
                x = x[:-1]
                y = y[:-1]

        elif re.search(endif_re, line):

            if x[-1] % 2 == 0:
                x[-1] += 1
                y[-1] = y[-2] + 1

                if x[-1] not in amount_per_branch:
                    amount_per_branch[x[-1]] = 0
                    beginning_of_split[x[-1]] = 0
                    branch_width[x[-1]] = 0

                if y[-1] not in layer_height:
                    layer_height[y[-1]] = draw.textsize(
                        "a", font=font)[1] + font_size

                chart_code.append({
                    "type": "Connector",
                    "content": "c",
                    "position": [x[-1], y[-1]],
                    "role": 'e'
                })

                amount_per_branch[x[-1]] += 1
                y[-1] += 1

            if amount_per_branch[x[-1] - 1] > amount_per_branch[x[-1]]:
                amount_per_branch[x[-2]] += amount_per_branch[x[-1] - 1]
                y[-2] = amount_per_branch[x[-1] -
                                          1] + beginning_of_split[x[-2]] + 1
            else:
                amount_per_branch[x[-2]] += amount_per_branch[x[-1]]
                y[-2] = amount_per_branch[x[-1]] + beginning_of_split[
                    x[-2]] + 1

            amount_per_branch[x[-1]] = 0
            amount_per_branch[x[-1] - 1] = 0

            y = y[:-1]
            x = x[:-1]

            chart_code.append({
                "type": "Connector",
                "content": "cB",
                "position": [x[-1], y[-1]],
                "role": 'cB'
            })

            amount_per_branch[x[-1]] += 1
            y[-1] += 1

        elif re.search(while_re, line):
            chart_code.append({
                "type": "Decision",
                "content": re.search(while_re, line).group(1),
                "position": [x[-1], y[-1]],
                "role": 'o'
            })

            if len(line) > len("IF") + 1:
                width = 3 / 2 * draw.textsize(line, font=font)[0]
                height = 5 * draw.textsize(line, font=font)[1]
            else:
                width = 5 * font_size
                height = 5 * font_size

            if width > branch_width[x[-1]]:
                branch_width[x[-1]] = width

            if height > layer_height[y[-1]]:
                layer_height[y[-1]] = height

            amount_per_branch[x[-1]] += 1

            beginning_of_split[x[-1]] = y[-1]

            x.append(2 * x[-1])
            y.append(y[-1] + 1)

        elif re.search(endwhile_re, line):

            x[-1] += 1
            y[-1] = y[-2] + 1

            if x[-1] not in amount_per_branch:
                amount_per_branch[x[-1]] = 0
                beginning_of_split[x[-1]] = 0
                branch_width[x[-1]] = 0

            if y[-1] not in layer_height:
                layer_height[y[-1]] = draw.textsize("a",
                                                    font=font)[1] + font_size

            chart_code.append({
                "type": "Connector",
                "content": "c",
                "position": [x[-1], y[-1]],
                "role": 'e'
            })

            amount_per_branch[x[-1]] += 1
            y[-1] += 1

            if amount_per_branch[x[-1] - 1] > amount_per_branch[x[-1]]:
                amount_per_branch[x[-2]] += amount_per_branch[x[-1] - 1]
                y[-2] = amount_per_branch[x[-1] -
                                          1] + beginning_of_split[x[-2]] + 1
            else:
                amount_per_branch[x[-2]] += amount_per_branch[x[-1]]
                y[-2] = amount_per_branch[x[-1]] + beginning_of_split[
                    x[-2]] + 1

            amount_per_branch[x[-1]] = 0
            amount_per_branch[x[-1] - 1] = 0

            y = y[:-1]
            x = x[:-1]
            chart_code.append({
                "type": "Connector",
                "content": "c",
                "position": [x[-1], y[-1]],
                "role": 'cW'
            })

            amount_per_branch[x[-1]] += 1
            y[-1] += 1

        else:
            chart_code.append({
                "type": "Process",
                "content": line,
                "position": [x[-1], y[-1]],
                "role": 'n'
            })

            if draw.textsize(
                    line, font=font)[0] + font_size * 2 > branch_width[x[-1]]:
                branch_width[x[-1]] = draw.textsize(
                    line, font=font)[0] + font_size * 2

            if draw.textsize(line,
                             font=font)[1] + font_size > layer_height[y[-1]]:
                layer_height[y[-1]] = draw.textsize(line,
                                                    font=font)[1] + font_size

            amount_per_branch[x[-1]] += 1
            y[-1] += 1

    del draw, img

    max_branch = 2**(floor(log(max(amount_per_branch), 2)) + 1) - 1

    max_y = amount_per_branch[1]

    return chart_code, max_branch, max_y, layer_height, branch_width


def drawer(chart_code, max_branch, max_y, layer_height, branch_width,
           font_data):

    def Terminator(text, position):

        width = draw.textsize(text, font=font)[0] + font_size * 2
        height = draw.textsize(text, font=font)[1] + font_size * 2

        x = width_offset + combined_widths[
            position[0]] + branch_width[position[0]] / 2 - width / 2
        y = combined_heights[position[1]]

        coords = [(x, y), (x + width, y + height)]

        draw.ellipse(coords, fill=None, outline="black")
        draw.text((x + font_size, y + height / 2 - scale_constant),
                  text,
                  fill='black',
                  font=font)

        return height

    def Decision(text, position):

        def diamond(coords, width, height):
            draw.line([(coords[0] + width / 2, coords[1]),
                       (coords[0] + width, coords[1] + height / 2)],
                      fill='black',
                      width=1)
            draw.line([(coords[0] + width / 2, coords[1]),
                       (coords[0], coords[1] + height / 2)],
                      fill='black',
                      width=1)

            draw.line([(coords[0], coords[1] + height / 2),
                       (coords[0] + width / 2, coords[1] + height)],
                      fill='black',
                      width=1)
            draw.line([(coords[0] + width, coords[1] + height / 2),
                       (coords[0] + width / 2, coords[1] + height)],
                      fill='black',
                      width=1)

        if len(text) > len("IF") + 1:
            width = 3 / 2 * draw.textsize(text, font=font)[0]
            height = 5 * draw.textsize(text, font=font)[1]
            text_offset = draw.textsize(text, font=font)[0] / 4

        else:
            width = 5 * font_size
            height = 5 * font_size
            text_offset = (width - draw.textsize(text, font=font)[0]) / 2

        x = width_offset + combined_widths[
            position[0]] + branch_width[position[0]] / 2 - width / 2
        y = combined_heights[position[1]]

        diamond((x, y), width, height)

        draw.text(
            (x + width / 2 - scale_constant, y + height / 4 - scale_constant),
            "IF",
            fill='black',
            font=font)
        draw.text((x + text_offset, y + height / 2 - scale_constant),
                  text,
                  fill='black',
                  font=font)

        return height, width

    def Process(text, position):

        width = draw.textsize(text, font=font)[0] + font_size * 2
        height = draw.textsize(text, font=font)[1] + font_size

        x = width_offset + combined_widths[
            position[0]] + branch_width[position[0]] / 2 - width / 2
        y = combined_heights[position[1]]

        coords = [(x, y), (x + width, y + height)]

        draw.rectangle(coords, fill=None, outline='black')
        draw.text((x + font_size, y + scale_constant),
                  text,
                  fill='black',
                  font=font)

        return height

    def IO(text, position):

        def parallelogram(coords, width, height, offset):
            draw.line([(coords[0], coords[1] + height),
                       (coords[0] + width, coords[1] + height)],
                      fill='black',
                      width=1)
            draw.line([(coords[0] + offset, coords[1]),
                       (coords[0] + width + offset, coords[1])],
                      fill='black',
                      width=1)

            draw.line([(coords[0] + offset, coords[1]),
                       (coords[0], coords[1] + height)],
                      fill='black',
                      width=1)
            draw.line([(coords[0] + width + offset, coords[1]),
                       (coords[0] + width, coords[1] + height)],
                      fill='black',
                      width=1)

        width = draw.textsize(text, font=font)[0] + font_size * 2
        height = draw.textsize(text, font=font)[1] + font_size
        offset = font_size

        x = width_offset + combined_widths[position[0]] + branch_width[
            position[0]] / 2 - width / 2 - offset / 2
        y = combined_heights[position[1]]

        parallelogram((x, y), width, height, offset)

        draw.text((x + font_size + offset / 2, y + scale_constant),
                  text,
                  fill='black',
                  font=font)

        return height

    def Flowline(role, position, height, chart_code, width):

        def arrow(coords, height, direction):
            h = int(height)
            L = int(height)
            if direction == "left":
                draw.line([(coords[0], coords[1]),
                           (coords[0] + L, coords[1] + h)],
                          fill='black',
                          width=1)
                draw.line([(coords[0], coords[1]),
                           (coords[0] + L, coords[1] - h)],
                          fill='black',
                          width=1)

            elif direction == "right":
                draw.line([(coords[0], coords[1]),
                           (coords[0] - L, coords[1] + h)],
                          fill='black',
                          width=1)
                draw.line([(coords[0], coords[1]),
                           (coords[0] - L, coords[1] - h)],
                          fill='black',
                          width=1)

            elif direction == "down":
                draw.line([(coords[0], coords[1]),
                           (coords[0] + L, coords[1] - h)],
                          fill='black',
                          width=1)
                draw.line([(coords[0], coords[1]),
                           (coords[0] - L, coords[1] - h)],
                          fill='black',
                          width=1)

            elif direction == "up":
                draw.line([(coords[0], coords[1]),
                           (coords[0] + L, coords[1] + h)],
                          fill='black',
                          width=1)
                draw.line([(coords[0], coords[1]),
                           (coords[0] - L, coords[1] + h)],
                          fill='black',
                          width=1)

        if role == 'n':
            axis = width_offset + combined_widths[
                position[0]] + branch_width[position[0]] / 2

            start = combined_heights[position[1]] + height
            distance = combined_heights[position[1] + 1] - start

            draw.line([(axis, start), (axis, start + distance)],
                      fill='black',
                      width=1)
            arrow([axis, start + 2 * distance / 3], block_gap / 3, "down")

        elif role == 'e':
            axis = width_offset + combined_widths[
                position[0]] + branch_width[position[0]] / 2

            start = combined_heights[position[1]]
            distance = combined_heights[position[1] + 1] - start

            draw.line([(axis, start), (axis, start + distance)],
                      fill='black',
                      width=1)

        elif role == 'o':
            if_axis = width_offset + combined_widths[
                position[0]] + branch_width[position[0]] / 2

            start = combined_heights[position[1]] + height / 2
            end = combined_heights[position[1] + 1]

            even_axis = width_offset + combined_widths[
                2 * position[0]] + branch_width[2 * position[0]] / 2
            odd_axis = width_offset + combined_widths[
                2 * position[0] + 1] + branch_width[2 * position[0] + 1] / 2

            draw.line([(if_axis - width / 2, start), (even_axis, start)],
                      fill='black',
                      width=1)
            arrow(
                [(even_axis + if_axis - width / 2) / 2 - block_gap / 3, start],
                block_gap / 3, "left")

            draw.line([(if_axis + width / 2, start), (odd_axis, start)],
                      fill='black',
                      width=1)
            arrow(
                [(odd_axis + if_axis + width / 2) / 2 + block_gap / 3, start],
                block_gap / 3, "right")

            draw.line([(even_axis, start), (even_axis, end)],
                      fill='black',
                      width=1)
            arrow([even_axis, (start + end) / 2 + block_gap / 3],
                  block_gap / 3, "down")

            draw.line([(odd_axis, start), (odd_axis, end)],
                      fill='black',
                      width=1)
            arrow([odd_axis, (start + end) / 2 + block_gap / 3], block_gap / 3,
                  "down")

            draw.text(((if_axis - width / 2 + even_axis) / 2 - block_gap / 2,
                       start - 2 * font_size),
                      "yes",
                      fill='black',
                      font=font)
            draw.text(((if_axis + width / 2 + odd_axis) / 2 - block_gap / 3,
                       start - 2 * font_size),
                      "no",
                      fill='black',
                      font=font)

        elif role == 'cW':
            axis = width_offset + combined_widths[
                position[0]] + branch_width[position[0]] / 2

            start = combined_heights[position[1]] + height / 2
            distance = combined_heights[position[1] + 1] - start

            even_branch = [position[0] * 2, 0]
            odd_branch = [position[0] * 2 + 1, 0]
            associated_while = [position[0], 0]

            for obj in reversed(chart_code):
                if obj['position'][0] == even_branch[0] and even_branch[1] == 0:
                    even_branch[1] = obj['position'][1]
                if obj['position'][0] == odd_branch[0] and odd_branch[1] == 0:
                    odd_branch[1] = obj['position'][1]
                if obj['position'][0] == associated_while[
                        0] and associated_while[1] == 0:
                    associated_while[1] = obj['position'][1]
                if even_branch[1] != 0 and associated_while[
                        1] != 0 and odd_branch[1] != 0:
                    break

            even_axis = width_offset + combined_widths[
                2 * position[0]] + branch_width[2 * position[0]] / 2

            draw.line([(axis, start), (even_axis, start)],
                      fill='black',
                      width=1)
            arrow([(axis + even_axis) / 2 - block_gap / 3, start],
                  block_gap / 3, "right")

            start = combined_heights[even_branch[1] + 1]
            distance = combined_heights[position[1]] + height / 2 - start

            draw.line([(even_axis, start), (even_axis, start + distance)],
                      fill='black',
                      width=1)

            while_height = combined_heights[associated_while[1] +
                                            1] - block_gap

            draw.line([(axis, while_height), (axis, start + distance)],
                      fill='black',
                      width=1)

            arrow(
                [axis, (while_height + start + distance) / 2 - block_gap / 3],
                block_gap / 3, "up")

            odd_axis = width_offset + combined_widths[
                2 * position[0] + 1] + branch_width[2 * position[0] + 1] / 2

            start = combined_heights[odd_branch[1]]
            distance = combined_heights[position[1]] + height - start

            draw.line([(odd_axis, start), (odd_axis, start + distance)],
                      fill='black',
                      width=1)

            draw.line([(odd_axis, start + distance), (axis, start + distance)],
                      fill='black',
                      width=1)
            arrow([(axis + odd_axis) / 2 - block_gap / 3, start + distance],
                  block_gap / 3, "left")

            draw.line([(axis, start + distance),
                       (axis, start + distance + block_gap)],
                      fill='black',
                      width=1)
            arrow([axis, start + distance + block_gap * 2 / 3], block_gap / 3,
                  "down")

        elif role == 'cB':
            axis = width_offset + combined_widths[
                position[0]] + branch_width[position[0]] / 2

            start = combined_heights[position[1]] + height / 2
            distance = combined_heights[position[1] + 1] - start

            draw.line([(axis, start), (axis, start + distance)],
                      fill='black',
                      width=1)
            arrow([axis, start + 2 * distance / 3], block_gap / 3, "down")

            even_branch = [position[0] * 2, 0]
            odd_branch = [position[0] * 2 + 1, 0]

            for obj in reversed(chart_code):
                if obj['position'][0] == odd_branch[0] and odd_branch[1] == 0:
                    odd_branch[1] = obj['position'][1]
                elif obj['position'][0] == even_branch[0] and even_branch[
                        1] == 0:
                    even_branch[1] = obj['position'][1]
                if even_branch[1] != 0 and odd_branch[1] != 0:
                    break

            even_axis = width_offset + combined_widths[
                2 * position[0]] + branch_width[2 * position[0]] / 2
            odd_axis = width_offset + combined_widths[
                2 * position[0] + 1] + branch_width[2 * position[0] + 1] / 2

            draw.line([(axis, start), (even_axis, start)],
                      fill='black',
                      width=1)
            arrow([(axis + even_axis) / 2 - block_gap / 3, start],
                  block_gap / 3, "right")

            draw.line([(axis, start), (odd_axis, start)],
                      fill='black',
                      width=1)
            arrow([(axis + odd_axis) / 2 + block_gap / 3, start],
                  block_gap / 3, "left")

            start = combined_heights[even_branch[1] + 1]
            distance = combined_heights[position[1]] + height / 2 - start

            draw.line([(even_axis, start), (even_axis, start + distance)],
                      fill='black',
                      width=1)

            start = combined_heights[odd_branch[1] + 1]
            distance = combined_heights[position[1]] + height / 2 - start

            draw.line([(odd_axis, start), (odd_axis, start + distance)],
                      fill='black',
                      width=1)

    font_path = font_data['path']
    font_size = font_data['size']
    font = ImageFont.truetype(font_path, font_size)

    scale_constant = int(font_size / 2)
    block_gap = font_size * 3 / 2

    height_offset = 2 * font_size
    width_offset = 2 * font_size

    tree = newTree([i for i in range(1, max_branch + 1)], "levelorder")

    tree_struct = tree.serializeInOrder(tree.root)

    combined_widths = {}

    for i in range(0, len(tree_struct)):
        branch = tree_struct[i]
        if i == 0:
            combined_widths[branch] = 0
        else:
            if tree_struct[i - 1] in branch_width.keys():
                combined_widths[branch] = combined_widths[tree_struct[
                    i - 1]] + branch_width[tree_struct[i - 1]]
            else:
                branch_width[tree_struct[i - 1]] = 0
                combined_widths[branch] = combined_widths[tree_struct[i -
                                                                      1]] + 0

    if tree_struct[-1] not in branch_width.keys():
        branch_width[tree_struct[-1]] = 0

    combined_heights = {}

    for key in layer_height.keys():
        if key == 1:
            combined_heights[key] = height_offset
        else:
            combined_heights[key] = layer_height[key - 1] + combined_heights[
                key - 1] + block_gap

    img_width = int(combined_widths[list(combined_widths.keys())[-1]] +
                    branch_width[list(combined_widths.keys())[-1]] +
                    width_offset * 2)
    img_height = int(combined_heights[max_y] + layer_height[max_y] +
                     height_offset)

    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)

    width = 0
    for i in range(0, len(chart_code)):
        block = chart_code[i]
        if block['type'] == 'IO':
            height = IO(block['content'], block['position'])
        elif block['type'] == 'Terminator':
            height = Terminator(block['content'], block['position'])
        elif block['type'] == 'Process':
            height = Process(block['content'], block['position'])
        elif block['type'] == 'Decision':
            height, width = Decision(block['content'], block['position'])
        elif block['type'] == 'Connector':
            height = draw.textsize("c", font=font)[1] + font_size

        Flowline(block['role'], block['position'], height, chart_code[0:i],
                 width)

    del draw

    return img

@click.command()
@click.option('--size', default=20, help="The size of the flowchart")
@click.option('--font', default=os.path.join(os.path.dirname(__file__), '..', 'fonts', 'NotoSans-Regular.ttf'), help="The font's path")
@click.option('--input-dir', default="../pseudo", help="Directory containing the pseudocode files")
@click.option('--output-dir', default="../../Code2Logic/flowcharts", help="Directory to save the output flowchart images")
def main(size, input_dir, output_dir, font):
    font_data = {"path": font, "size": size}

    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_input_dir = os.path.abspath(os.path.join(script_dir, input_dir))
    abs_output_dir = os.path.abspath(os.path.join(script_dir, output_dir))

    os.makedirs(abs_output_dir, exist_ok=True)

    print(f"Input directory: {abs_input_dir}")
    print(f"Output directory: {abs_output_dir}")

    for filename in os.listdir(abs_input_dir):
        if filename.endswith(".txt"):
            input_file_path = os.path.join(abs_input_dir, filename)
            output_file_path = os.path.join(abs_output_dir, "flowchart_" + os.path.splitext(filename)[0] + ".png")

            print(f"Processing {input_file_path} -> {output_file_path}")

            lines = read(input_file_path)
            print(f"Read {len(lines)} lines from {input_file_path}")

            chart_code, max_branch, max_y, layer_height, branch_width = translation(lines, font_data)
            print("Translation complete.")

            flowchart = drawer(chart_code, max_branch, max_y, layer_height, branch_width, font_data)
            print("Flowchart drawing complete.")

            flowchart.save(output_file_path)
            print(f"Saved flowchart to {output_file_path}")

if __name__ == '__main__':
    main()
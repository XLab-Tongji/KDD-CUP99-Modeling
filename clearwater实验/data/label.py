#!/usr/bin/env python
# -*- coding:utf-8 -*-

import xlrd
import xlwt 
import argparse


def parse_xlsx(file):
    '''
    读入excel到lines，lines[0]为titles
    '''
    workbook = xlrd.open_workbook(file)
    sheet = workbook.sheet_by_index(0)
    lines = []
    for i in range(sheet.nrows):
        lines.append(sheet.row_values(i)) 
        # For test rain.
        # if i > 2:
        #     break
    return lines


def parse_log(file):
    '''
    读入log到rule，用于判断时间所属时间段label
    '''
    rule = []
    lines = []
    with open(file, 'r') as file:
        temp_lines = file.readlines()
        for line in temp_lines:
            if '->' in line:
                continue
            lines.append(line[:-1])
    
    for line in lines:
        if '1 start normal' in line:
            start1 = line.split(' ')[3]
        elif '1 stop normal' in line:
            stop1 = line.split(' ')[3]
        elif '2 start cpu' in line:
            start2 = line.split(' ')[3]
        elif '2 stop cpu' in line:
            stop2 = line.split(' ')[3]
        elif '3 start normal' in line:
            start3 = line.split(' ')[3]
        elif '3 stop normal' in line:
            stop3 = line.split(' ')[3]
        elif '4 start mem' in line:
            start4 = line.split(' ')[3]
        elif '4 stop mem' in line:
            stop4 = line.split(' ')[3]
        elif '5 start normal' in line:
            start5 = line.split(' ')[3]
        elif '5 stop normal' in line:
            stop5 = line.split(' ')[3]
        elif '6 start io' in line:
            start6 = line.split(' ')[3]
        elif '6 stop io' in line:
            stop6 = line.split(' ')[3]
        elif '7 start normal' in line:
            start7 = line.split(' ')[3]
        elif '7 stop normal' in line:
            stop7 = line.split(' ')[3]
 
    rule.append({'start':start1, 'stop':stop1, 'label':'normal'})
    rule.append({'start':start2, 'stop':stop2, 'label':'cpu'})
    rule.append({'start':start3, 'stop':stop3, 'label':'normal'})
    rule.append({'start':start4, 'stop':stop4, 'label':'mem'})
    rule.append({'start':start5, 'stop':stop5, 'label':'normal'})
    rule.append({'start':start6, 'stop':stop6, 'label':'io'})
    rule.append({'start':start7, 'stop':stop7, 'label':'normal'})
    return rule


def check_stage(line, rule):
    '''
    对每一行数据打标签，并返回
    '''
    time = line[1]
    label = None
    for obj in rule:
        if long(time) >= long(obj['start']) and long(time) <= long(obj['stop']):
            label = obj['label']

    if label != None:
        if label == 'normal':
            line += ['1', '0', '0', '0']
        elif label == 'cpu':
            line += ['0', '1', '0', '0']
        elif label == 'mem':
            line += ['0', '0', '1', '0']
        elif label == 'io':
            line += ['0', '0', '0', '1']
    else:
        line += ['1', '0', '0', '0']
    return line


def generate_label_file(lines, rule):
    '''
    根据lines、rule，生成带标签数据集并写入当前目录
    '''
    label_lines = []
    # 首行
    line1 = lines[0] + [u'normal', u'cpu', u'mem', u'io']
    label_lines.append(line1)
    
    # 打标签
    for i in range(1, len(lines)):
        label_lines.append(check_stage(lines[i], rule))
    
    # 写excel
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('data-labeled')

    # i -> row
    # j -> col
    for i in range(len(label_lines)):
        for j in range(len(label_lines[i])):
            sheet.write(i, j, label_lines[i][j])
    return wbk


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_xlsx", help="specify input excel file")
    parser.add_argument("input_log", help="specify input stress log file")
    args = parser.parse_args()

    # 读入原始数据集
    lines = parse_xlsx(args.input_xlsx)

    # 读入压测日志
    rule = parse_log(args.input_log)

    # 生成标签数据集
    wbk = generate_label_file(lines, rule)

    # 写入文件
    wbk.save('%s-labeled.xls' % args.input_xlsx[:-5])


if __name__ == '__main__':
    main()

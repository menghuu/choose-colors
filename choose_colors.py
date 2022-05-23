#!/usr/bin/env python

import random
from typing import Set, Union, Tuple, List, Dict

from pathlib import Path
import math

from sklearn.cluster import KMeans
from converters import rgb2lab, lab2rgb, rgb2hsl, compute_lab_distance
import pandas as pd

from argparse import ArgumentParser
import pprint


def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{}\033[0m".format(r, g, b, text)


def read_colors(filepath: Union[str, Path]):
    names = []
    colors = []
    df = pd.DataFrame(columns=['colorname', 'r', 'g', 'b', 'rgbcode', 'colorful_rgbcode', 'lab_l', 'lab_a', 'lab_b', 'hsl_h', 'hsl_s', 'hsl_l'])
    with open(filepath) as f:
        for line in f.readlines():
            elems = line.split(':')
            if len(elems) == 0:
                continue
            colorname = elems[0].strip('" \n\t')
            if len(elems) == 1:
                colorstring = colorname
            else:
                colorstring = elems[1]
            colorstring = colorstring.strip('# "\n\t')
            r = int(colorstring[:2], 16)
            g = int(colorstring[2:4], 16)
            b = int(colorstring[4:], 16)
            colors.append([r, g, b])
            names.append(colorname)
            lab = rgb2lab(r, g, b)
            hsl = rgb2hsl(r, g, b)
            df.loc[len(df)] = {
                'colorname': colorname,
                'r': r,
                'g': g,
                'b': b,
                'rgbcode': '#' + colorstring,
                'colorful_rgbcode': colored(r, g, b, '#' + colorstring),
                'lab_l': lab[0],
                'lab_a': lab[1],
                'lab_b': lab[2],
                'hsl_h': hsl[0],
                'hsl_s': hsl[1],
                'hsl_l': hsl[2]
            }
            
    # 为什么转化成uint8？ 答：因为skimage的例子中的图片是uint8，
    # 而且如果不转成uint8，则rgb转化lab会失败！！出现奇特的结果
    # color.rgb2lab(np.array([[255, 125, 5]]).astype(np.uint8)) 结果是 array([[66.47746889, 44.33420768, 72.94181697]])
    # 这与使用 converters.py 的计算结果差不多：66.47266912541974, 44.33885551261418, 72.95017150952644
    # http://www.easyrgb.com/en/convert.php 网站的计算结果是：66.477   44.335   72.942
    # 但是 color.rgb2lab([[255, 125, 5]]) 的结果是 array([[0., 0., 0.]])
    # 甚至 color.rgb2lab(np.array([[255, 125, 5]])) 结果是 array([[0., 0., 0.]])
    # np.array([[255, 125, 5]]).dtype 是 dtype('int64')

    # colors = np.array(colors).astype(np.uint8) # shape nx3
    
    return names, colors, df


def get_cluster_id(labcolors, scores=None, num=16, random_seed=42):
    if not scores:
        scores = [1] * len(labcolors)
    kmeans = KMeans(n_clusters=num, random_state=random_seed)
    labels = kmeans.fit_predict(labcolors, sample_weight=scores)
    return labels


def choose_cluster_color_by_lab_center(df: pd.DataFrame) -> pd.DataFrame:
    df_with_center_lab = df.copy()
    df_with_center_lab['is_choosen'] = False
    df_with_center_lab['center_l'] = None
    df_with_center_lab["center_a"] = None
    df_with_center_lab["center_b"] = None
    df_with_center_lab['distance'] = None

    cluster_ids = df_with_center_lab.cluster_id.unique()

    for cluster_id in cluster_ids:
        one_group_df = df_with_center_lab[df_with_center_lab.cluster_id == cluster_id]
        center_lab = (one_group_df.lab_l.mean(), one_group_df.lab_a.mean(), one_group_df.lab_b.mean())

        df_with_center_lab.loc[df_with_center_lab.cluster_id == cluster_id, 'center_l'] = center_lab[0]
        df_with_center_lab.loc[df_with_center_lab.cluster_id == cluster_id, 'center_a'] = center_lab[1]
        df_with_center_lab.loc[df_with_center_lab.cluster_id == cluster_id, 'center_b'] = center_lab[2]

        index_vs_distance = {}
        for index, series in one_group_df.iterrows():
            distance = compute_lab_distance(center_lab, series[['lab_l', 'lab_a', 'lab_b']].tolist())
            index_vs_distance[index] = distance
            df_with_center_lab.loc[index, 'distance'] = distance
        sorted_indexes = sorted(index_vs_distance.keys(), key=lambda x: index_vs_distance[x])
        min_index = sorted_indexes[0]
        df_with_center_lab.loc[min_index, 'is_choosen'] = True

    return df_with_center_lab


def choose_cluster_color_by_lab_lcenter(df: pd.DataFrame):
    cluster_ids = df.cluster_id.unique()
    df['is_choosen'] = False
    for cluster_id in cluster_ids:
        onegroup = df[df.cluster_id == cluster_id]
        choosen_index = onegroup.sort_values(by='lab_l').iloc[len(onegroup) // 2].index.to_list()[0]
        df.loc[choosen_index, 'is_choosen'] = True
    
    return df

def choose_cluster_color_by_other(df: pd.DataFrame, by='lab_l', number=0):
    cluster_ids = df.cluster_id.unique()
    df['is_choosen'] = False
    for cluster_id in cluster_ids:
        onegroup = df[df.cluster_id == cluster_id]
        elements = onegroup[by].tolist()
        sorte_indexes = sorted(range(len(elements)), key=lambda index: abs(elements[index] - number))
        index = sorte_indexes[0]
        choosen_index = onegroup.iloc[index].name
        df.loc[choosen_index, 'is_choosen'] = True
    
    return df

  

def get_args():
    parser = ArgumentParser(
        description='''
        choose colors based on the degree of differentiation. NOTE: the colors choosen by this program have strong contrast!!
        根据颜色的区分度来选择颜色。注意：本程序所选出来的颜色普遍差别很大
    ''')
    parser.add_argument('-i', '--color-corpus', required=True)
    parser.add_argument('-t', '--color-corpus-name', default='default-colors')
    parser.add_argument('-r', '--random-seed', default=42, type=int)

    parser.add_argument('-n', '--number-choosen-colors', type=int, default=16)
    parser.add_argument('-g', '--cluster-by',choices=['lab', 'lab_l', 'lab_a', 'lab_b'], default='lab')
    parser.add_argument(
        '-c','--choose-by', default='hsl_s0', 
        choices=['lab_l0', 'lab_l50', 'lab_l100', 'lab_lcenter', 'lab_center', 'hsl_s0'],
        help=\
        '''
        lab_10: choose the lowest luminance color of one cluster; 分组后选择组内亮度最低的颜色;
        lab_l50: choose the medium luminance color of one cluster; 分组后选择组内中间亮度的颜色;
        lab_1100: choose the higher luminance color of one cluster; 分组后选择组内亮度最高的颜色;
        lab_center: choose the center lab-color of one cluster; 分组后选择组内的中间的颜色;
        hsl_s0: choose the lower saturation choose the color of one cluster; 分组后选择组内饱和度最低的颜色;
        hsl_s0.5: choose the medium saturation choose the color of one cluster; 分组后选择组内饱和度中间的颜色;
        hsl_s1: choose the higher saturation choose the color of one cluster; 分组后选择组内饱和度最高的颜色;
        '''
    )
    parser.add_argument(
        '-s', '--sort-by', choices=['lab_l', 'hsl_s'], default='lab_l',
        help='''
        It has nothing to do with color selection, but with the color sorting of the output; 此选项与分组和选择没啥关系，只是影响输出的排序;
        lab_l: sorted by luminance; 根据亮度排序;
        hsl_s: sorted by saturation; 根据饱和度排序;
        '''
    )

    parser.add_argument('-o', '--output-color-palette')

    args = parser.parse_args()

    return args


def main():
    cli_args = get_args()

    filepath = Path(cli_args.color_corpus)
    if not filepath.exists():
        raise FileNotFoundError('cannot found color-corpus file path ' + filepath)

    number_choosen_colors = cli_args.number_choosen_colors
    color_corpus_name = cli_args.color_corpus_name
    cluster_by = cli_args.cluster_by

    # read the corpus
    colornames, rgbcolors, colordf = read_colors(filepath)

    # cluster by
    if cluster_by == 'lab':
        cluster_by_columns = ['lab_l', 'lab_a', 'lab_b']
    else:
        cluster_by_columns = [cluster_by]
    cluster_id = get_cluster_id(colordf[cluster_by_columns], num=number_choosen_colors, random_seed=cli_args.random_seed)
    colordf['cluster_id'] = cluster_id

    # choose by
    choose_by = cli_args.choose_by
    if choose_by == 'lab_center':
        colordf = choose_cluster_color_by_lab_center(colordf)
    elif choose_by == 'lab_lcenter':
        colordf = choose_cluster_color_by_lab_lcenter(colordf)
    else:
        if choose_by.startswith('lab_l'):
            by = 'lab_l'
        else:
            by = 'hsl_s'
        number = int(choose_by[len(by):])
        colordf = choose_cluster_color_by_other(colordf, by=by, number=number)

    # sort by
    sort_by = cli_args.sort_by

    choosen_colordf = colordf[colordf.is_choosen].sort_values(by=sort_by)
    print('infomations are:')
    pprint.pprint(vars(cli_args))
    print('choosen colors are: ')
    print(choosen_colordf[['colorname', 'lab_l', 'lab_a', 'lab_b', 'hsl_h', 'hsl_s', 'hsl_l', 'colorful_rgbcode']].to_string())

    # output
    output_color_palette = cli_args.output_color_palette
    if output_color_palette:
        with open(output_color_palette, mode='wt') as f:
            for _, series in choosen_colordf.iterrows():
                f.write(f'{series.colorname}: "{series.rgbcode}"\n')
    

if __name__ == '__main__':
    main()

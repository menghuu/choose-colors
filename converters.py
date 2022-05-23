#!/usr/bin/env python

"""
此文件是根据 http://www.easyrgb.com/en/math.php 写的转化器

注意！！ 如果使用skimage的话, 需要将rgb数据转化成 uint8 类型！！！ 
别的类型(比如默认的np.int64, 或者np.float16)会计算错误，至少和这里的代码以及上述网站的计算结果不一样！
"""

import math
from typing import Union, Tuple, List


def rgb2xyz(r, g, b):

    # see http://www.easyrgb.com/en/math.php
    var_R = r / 255
    var_G = g / 255
    var_B = b / 255

    if var_R > 0.04045:
        var_R = ((var_R + 0.055) / 1.055) ** 2.4
    else:
        var_R = var_R / 12.92

    if var_G > 0.04045:
        var_G = ((var_G + 0.055) / 1.055) ** 2.4
    else:
        var_G = var_G / 12.92

    if var_B > 0.04045:
        var_B = ((var_B + 0.055) / 1.055) ** 2.4
    else:
        var_B = var_B / 12.92
    var_R = var_R * 100
    var_G = var_G * 100
    var_B = var_B * 100

    X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
    Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
    Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505
    return X, Y, Z


def xyz2rgb(x, y, z):
    var_X = x / 100
    var_Y = y / 100
    var_Z = z / 100

    var_R = var_X * 3.2406 + var_Y * -1.5372 + var_Z * -0.4986
    var_G = var_X * -0.9689 + var_Y * 1.8758 + var_Z * 0.0415
    var_B = var_X * 0.0557 + var_Y * -0.2040 + var_Z * 1.0570

    if (var_R > 0.0031308):
        var_R = 1.055 * (var_R ** (1 / 2.4)) - 0.055
    else:
        var_R = 12.92 * var_R
    if (var_G > 0.0031308):
        var_G = 1.055 * (var_G ** (1 / 2.4)) - 0.055
    else:
        var_G = 12.92 * var_G
    if (var_B > 0.0031308):
        var_B = 1.055 * (var_B ** (1 / 2.4)) - 0.055
    else:
        var_B = 12.92 * var_B

    sR = var_R * 255
    sG = var_G * 255
    sB = var_B * 255

    return int(sR), int(sG), int(sB)


def xyz2lab(x, y, z) -> Tuple[float, float, float]:
    # 使用D65作为标准光源， 参见
    # https://en.wikipedia.org/wiki/CIELAB_color_space
    # https://en.wikipedia.org/wiki/Illuminant_D65
    # https://en.wikipedia.org/wiki/Standard_illuminant#Illuminant_series_D
    # https://www.chem17.com/tech_news/detail/2735922.html
    # 而且 rgb2xyz使用的是 D65/2° standard illuminant ，大概可能需要一致吧

    Reference_X = 95.0489
    Reference_Y = 100
    Reference_Z = 108.8840

    var_X = x / Reference_X
    var_Y = y / Reference_Y
    var_Z = z / Reference_Z

    if (var_X > 0.008856):
        var_X = var_X ** (1/3)
    else:
        var_X = (7.787 * var_X) + (16 / 116)
    if (var_Y > 0.008856):
        var_Y = var_Y ** (1/3)
    else:
        var_Y = (7.787 * var_Y) + (16 / 116)
    if (var_Z > 0.008856):
        var_Z = var_Z ** (1/3)
    else:
        var_Z = (7.787 * var_Z) + (16 / 116)

    CIE_L = (116 * var_Y) - 16
    CIE_a = 500 * (var_X - var_Y)
    CIE_b = 200 * (var_Y - var_Z)

    return CIE_L, CIE_a, CIE_b


def lab2xyz(l, a, b):
    var_Y = (l + 16) / 116
    var_X = a / 500 + var_Y
    var_Z = var_Y - b / 200

    if (var_Y ** 3 > 0.008856):
        var_Y = var_Y ** 3
    else:
        var_Y = (var_Y - 16 / 116) / 7.787
    if (var_X ** 3 > 0.008856):
        var_X = var_X ** 3
    else:
        var_X = (var_X - 16 / 116) / 7.787
    if (var_Z ** 3 > 0.008856):
        var_Z = var_Z ** 3
    else:
        var_Z = (var_Z - 16 / 116) / 7.787

    Reference_X = 95.0489
    Reference_Y = 100
    Reference_Z = 108.8840

    X = var_X * Reference_X
    Y = var_Y * Reference_Y
    Z = var_Z * Reference_Z

    return X, Y, Z


def rgb2lab(r, g, b):
    return xyz2lab(*rgb2xyz(r, g, b))

def lab2rgb(l, a, b):
    return xyz2rgb(*lab2xyz(l, a, b))


def rgb2hsl(r, g, b):
    R, G, B = r, g, b 
    var_R = ( R / 255 )
    var_G = ( G / 255 )
    var_B = ( B / 255 )

    var_Min = min( var_R, var_G, var_B )   
    var_Max = max( var_R, var_G, var_B )  
    del_Max = var_Max - var_Min 

    L = ( var_Max + var_Min )/ 2

    if ( del_Max == 0 ):
        H = 0
        S = 0
        return H, S, L

    if ( L < 0.5 ):
        S = del_Max / ( var_Max + var_Min )
    else:
        S = del_Max / ( 2 - var_Max - var_Min )

    del_R = ( ( ( var_Max - var_R ) / 6 ) + ( del_Max / 2 ) ) / del_Max
    del_G = ( ( ( var_Max - var_G ) / 6 ) + ( del_Max / 2 ) ) / del_Max
    del_B = ( ( ( var_Max - var_B ) / 6 ) + ( del_Max / 2 ) ) / del_Max

    if ( var_R == var_Max ):
       H = del_B - del_G
    elif ( var_G == var_Max ):
       H = ( 1 / 3 ) + del_R - del_B
    elif ( var_B == var_Max ):
       H = ( 2 / 3 ) + del_G - del_R

    if ( H < 0 ): H += 1
    if ( H > 1 ): H -= 1

    return H, S, L



def compute_lab_distance(lab1: Tuple[float, float, float], lab2: Tuple[float, float, float]):
    delta_e = math.sqrt(
        (lab1[0] - lab2[0]) ** 2 + 
        (lab1[1] - lab2[1]) ** 2 + 
        (lab1[2] - lab2[2]) ** 2
    )
    return delta_e
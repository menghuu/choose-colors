# Make your palette, theme 制作你的调色盘、主题

Principle: After converting RGB colors into lab colors, cluster them into a designated group, and select a color for each group, which can be the center color of the color in the group or the lowest saturation in the group, etc

原理：将RGB色彩转化成lab色彩后，聚类成指定小组，每组选择一个颜色，依据可以是组内的颜色的中心颜色或者组内饱和度最低等等


```sh
# example
python choose_colors.py -i ./zhongguose.txt -t chinavid-chinese-colors -n 16 -g lab -c hsl_s0 -s lab_l -r 42

python choose_colors.py -i ./zhongguose.txt -t chinavid-chinese-colors -n 16 -g lab_l -c lab_l50 -s lab_l

# almost grey
python choose_colors.py -i ./zhongguose.txt -t chinavid-chinese-colors -n 16 -g lab_l -c hsl_s0 -s lab_l

# use `-o` to save the colorname and the rgbcode into file 
```

# color corpus file format 输入颜色文件的格式

- one column: rgbcode(with `#` or not), see `chinavid_colors.txt`
  - 如果是一列的话，那就应该是一列rgbcode，参见`chinavid_colors.txt`
- two columns: first is colorname; second is rbgcode(with `#` or not) see `zhongguose.txt`
  - 如果是两列的话，第一列是颜色名称，第二列是rgbcode，参见 `zhongguose.txt`

NOTE: remove blank line
注意：删除空白行


# useage 用法

```sh
❯ python choose_colors.py --help
usage: choose_colors.py [-h] -i COLOR_CORPUS [-t COLOR_CORPUS_NAME] [-r RANDOM_SEED] [-n NUMBER_CHOOSEN_COLORS] [-g {lab,lab_l,lab_a,lab_b}]
                        [-c {lab_l0,lab_l50,lab_l100,lab_lcenter,lab_center,hsl_s0}] [-s {lab_l,hsl_s}] [-o OUTPUT_COLOR_PALETTE]

choose colors based on the degree of differentiation. NOTE: the colors choosen by this program have strong contrast!! 根据颜色的区分度来选择颜色。注意：本程序所选出来的颜色普遍差别很大

optional arguments:
  -h, --help            show this help message and exit
  -i COLOR_CORPUS, --color-corpus COLOR_CORPUS
  -t COLOR_CORPUS_NAME, --color-corpus-name COLOR_CORPUS_NAME
  -r RANDOM_SEED, --random-seed RANDOM_SEED
  -n NUMBER_CHOOSEN_COLORS, --number-choosen-colors NUMBER_CHOOSEN_COLORS
  -g {lab,lab_l,lab_a,lab_b}, --cluster-by {lab,lab_l,lab_a,lab_b}
  -c {lab_l0,lab_l50,lab_l100,lab_lcenter,lab_center,hsl_s0}, --choose-by {lab_l0,lab_l50,lab_l100,lab_lcenter,lab_center,hsl_s0}
                        lab_10: choose the lowest luminance color of one cluster; 分组后选择组内亮度最低的颜色; lab_l50: choose the medium luminance color of one cluster; 分组后选择组内 中间亮度的颜色; lab_1100:
                        choose the higher luminance color of one cluster; 分组后选择组内亮度最高的颜色; lab_center: choose the center lab-color of one cluster; 分组后选择组内的中间的颜色; hsl_s0: choose the
                        lower saturation choose the color of one cluster; 分组后选择组内饱和度最低的颜色; hsl_s0.5: choose the medium saturation choose the color of one cluster; 分组后选择组内饱和度中间的颜色;
                        hsl_s1: choose the higher saturation choose the color of one cluster; 分组后选择组内饱和度最高的颜色;
  -s {lab_l,hsl_s}, --sort-by {lab_l,hsl_s}
                        It has nothing to do with color selection, but with the color sorting of the output; 此选项与分组和选择没啥关系，只是影响输出的排序; lab_l: sorted by luminance;  根据亮度排序; hsl_s: sorted
                        by saturation; 根据饱和度排序;
  -o OUTPUT_COLOR_PALETTE, --output-color-palette OUTPUT_COLOR_PALETTE

```

# some useful color website and js code to grab all colors

- https://www.chinavid.com/jp-color.html
- https://www.chinavid.com/chinese-color.html
```js
let spans = document.querySelectorAll('.container li span')
let colors = []
for (i=0; i<spans.length; i++) {
  color = spans[i].textContent
  colors.push(color)
  console.log(color)
 }
```


- http://zhongguose.com
```js
let aas = document.querySelectorAll('#colors li a')
let name_vs_color = []
for (i=0;i<aas.length; i++) {
  colorname = aas[i].querySelector('.name').innerText
  rgb = aas[i].querySelector('.rgb').innerText
  name_vs_color.push(colorname + ': ' + rgb)
}
```

# some useful links

- http://www.easyrgb.com/en/convert.php
- https://www.zhihu.com/question/30491221
- http://zhongguose.com/#tanzi
- https://www.xrite.com/blog/lab-color-space
- https://www.chinavid.com/chinese-color.html
- https://www.chinavid.com/jp-color.html
- https://github.com/chriskempson/base16
- https://en.wikipedia.org/wiki/CIELAB_color_space


# 依赖

```sh
pip install pandas scikit-learn
```

- `pandas` for manipulate datas
- `scikit-learn` for cluster colors
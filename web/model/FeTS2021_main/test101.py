import os
fname = r'./data/nifti/val\x\BraTS2021_00024_t1.nii.gz'
fname = fname.replace('\\','/')
dir_out = r'./data/nifti/output/'
newf = fname.split('/')[-1][:-10] + '.nii.gz'
f_new = os.path.join(dir_out, fname.split('/')[-1][:-10] + '.nii.gz')
print(f_new)


# -*- coding : UTF-8 -*-
# @file   : rd_niigz.py
# @Time   : 2021-09-14 17:40
# @Author : wmz
# encoding=utf8
'''
查看和显示nii文件
'''

import matplotlib

matplotlib.use('TkAgg')

from matplotlib import pylab as plt
import nibabel as nib
from nibabel import nifti1
from nibabel.viewers import OrthoSlicer3D
# 文件名，nii或nii.gz


img = nib.load(f_new)
print(img)
print(img.header['db_name'])  # 输出头信息
# shape不一定只有三个参数，打印出来看一下
width, height, queue = img.dataobj.shape
# 显示3D图像
OrthoSlicer3D(img.dataobj).show()

num = 1
# 按照10的步长，切片，显示2D图像
for i in range(0, queue, 10):
    img_arr = img.dataobj[:, :, i]
    plt.subplot(5, 4, num)
    plt.imshow(img_arr, cmap='gray')
    num += 1

plt.show()


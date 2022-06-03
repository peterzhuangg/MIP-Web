# -*- coding: utf-8 -*-
# https://github.com/kamleshpawar17/FeTS2021
#import matplotlib.pyplot as plt
import numpy as np
import SimpleITK as sitk
import time
import os
def process_nifiti_image_1(filepath,outputpath): # test method
    
    path = filepath
    #read nifiti image
    print('start process1')
    time.sleep(6)
    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    reader.SetFileName(path)
    image = reader.Execute();
    origin =image.GetOrigin()
    direction = image.GetDirection()
    space = image.GetSpacing()
    # print(origin)
    # print(direction)
    # print(space)
    image_arr=sitk.GetArrayFromImage(image)
    # print(type(image_arr))
    # print(image_arr.shape)
    #process
    # sampleimg=image_arr[85,:,:]
    img=(image_arr-np.min(image_arr))/(np.max(image_arr)-np.min(image_arr))
    # sampleimg2=img[85,:,:]
    #show image
    # plt.imshow(sampleimg, cmap = 'gray')
    # plt.show()
    # plt.imshow(sampleimg2, cmap = 'gray')
    # plt.show()
    rename = './'+ outputpath.split(".", 1)[1].split(".", 1)[0] + '_success_test' + '.nii.gz'
    f_old = './'+ outputpath.split(".", 1)[1].split(".", 1)[0] + '_Procssing_test.txt'
    if os.path.isfile(f_old):
        os.remove(f_old)
    # writer = sitk.ImageFileWriter()
    # writer.SetFileName(filepath + '/'+ rename)
    # writer.Execute(img)
    savedImg = sitk.GetImageFromArray(img)
    savedImg.SetOrigin(origin)
    savedImg.SetDirection(direction)
    savedImg.SetSpacing(space)
    sitk.WriteImage(savedImg, rename)
    #nib.save(new_img, filepath)
    print('finish process1')

    
# NII_DIR ='F:/Monash/FYP/FLASKproject/web/users/123'

# process_image(NII_DIR,'BraTS2021_00024_t1.nii.gz')
def process_nifiti_image_2(filepath):
    
    path = filepath
    #read nifiti image
    print('start process2')
    time.sleep(6)
    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    reader.SetFileName(path)
    image = reader.Execute();
    origin =image.GetOrigin()
    direction = image.GetDirection()
    space = image.GetSpacing()
    # print(origin)
    # print(direction)
    # print(space)
    image_arr=sitk.GetArrayFromImage(image)
    # print(type(image_arr))
    # print(image_arr.shape)
    #process
    # sampleimg=image_arr[85,:,:]
    img=(image_arr-np.min(image_arr))/(np.max(image_arr)-np.min(image_arr))
    # sampleimg2=img[85,:,:]
    #show image
    # plt.imshow(sampleimg, cmap = 'gray')
    # plt.show()
    # plt.imshow(sampleimg2, cmap = 'gray')
    # plt.show()
    rename = 'F:\Monash\FYP\FLASKproject\web'+ path.split(".", 1)[1].split(".", 1)[0] + '_success_ML1' + '.nii.gz'
    # writer = sitk.ImageFileWriter()
    # writer.SetFileName(filepath + '/'+ rename)
    # writer.Execute(img)
    savedImg = sitk.GetImageFromArray(img)
    savedImg.SetOrigin(origin)
    savedImg.SetDirection(direction)
    savedImg.SetSpacing(space)
    sitk.WriteImage(savedImg, rename)
    #nib.save(new_img, filepath)
    print('finish process2')

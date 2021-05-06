#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modified on Wed May 05 08:58:46 2021

@author: Felipe Jaramillo
"""
import os
import glob
import sys
import cv2
import numpy as np
import time

import h5py
import random

#------------------------------------------------------------------------------------------------------
# Angular downsampling from original subaperture images of each light field,
# - angular downsampled subaperture images synthesizing
# - angular upsampled via nearest, bicubic and lanczos subaperture images synthesizing
# - angular downsampled and original light field structure stuv synthesizing (for visual purposes)
# - angular downsampled, original and upsampled subaperture images video synthesizing (for visual purposes)

def LFuvst(imgs, st_hr, pth_LFuvst, folder):
  # Construct a spatial image with each spatial point compund by the angular
  # matrix corresponding to that u,v coordinate
  lfimg = np.zeros((imgs[0].shape[0]*st_hr, imgs[0].shape[1]*st_hr, 3), np.uint8)
  for u in range(imgs[0].shape[0]):
    print('.', end="")
    for v in range(imgs[0].shape[1]):
      i = 0
      for s in range(st_hr):
        for t in range(st_hr):
          img = imgs[i]
          lfimg[(u*st_hr+s),(v*st_hr+t), :] = img[u, v, :]
          i += 1
  if not os.path.exists(pth_LFuvst+folder):
    os.makedirs(pth_LFuvst+folder)
  name = pth_LFuvst + folder + '/' + folder + '_stuv.png'
  cv2.imwrite(name, lfimg)

def AngularDownsampling(imgs, st_hr, st_lr):

  dwnfactor = int(st_hr/st_lr)
  # Extract angular matrices for a single spatial point and then downsampling it
  ang_mtx = []
  nearest_ang_mtx = []
  bicubic_ang_mtx = []
  lanczos_ang_mtx = []
  height = imgs[0].shape[0]
  width = imgs[0].shape[1]
  for u in range(height):
    print('.', end="")
    for v in range(width):
      a_mtx = np.zeros((st_hr, st_hr, 3), np.uint8)
      i = 0
      for s in range(st_hr):
        for t in range(st_hr):
          img = imgs[i]
          a_mtx[s, t, :] = img[u, v, :]
          i += 1
      # angular downsampling
      fx = 1/dwnfactor
      fy = 1/dwnfactor
      amtx = cv2.resize(a_mtx, None, fx=fx, fy=fy, interpolation=cv2.INTER_AREA)
      ang_mtx.append(amtx)

      amtx = (np.float32(amtx) / 127.5) - 1 # Normalization between [-1, 1]
      amtx = np.uint8((amtx + 1) * 127.5)
      
      nr = cv2.resize(amtx, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
      bc = cv2.resize(amtx, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
      lc = cv2.resize(amtx, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)    
      nearest_ang_mtx.append(nr)
      bicubic_ang_mtx.append(bc)
      lanczos_ang_mtx.append(lc)

  return ang_mtx, nearest_ang_mtx, bicubic_ang_mtx, lanczos_ang_mtx

def SynthesizeImgs(a_mtxdwn, st_hr, h, w, pth_frames, folder, indx):  
  '''
  Function to synthesize and save the new sub-aperture images from the angular
  upsampled matrices of the corresponding LF
  '''
  imgs_new = []
  for s in range(st_hr):
    for t in range(st_hr):
      img = np.zeros((int(h), int(w), 3), np.uint8)
      i = 0
      for u in range(int(h)):
        for v in range(int(w)):
          img[u, v, :] = a_mtxdwn[i][s, t, :]
          i += 1
      print('.', end="")
      imgs_new.append(img)

  if indx == 'adownsampled':
    # Path to save original LF organized by stuv coordinates
    pth_LFuvst = os.getcwd() + '/LF/LF_stuv/'
    print("Saving angular downsampled light field structure stuv into %s " % ((pth_LFuvst+folder+'_'+indx)), end="")
    LFuvst(imgs_new, st_lr, pth_LFuvst, (folder+'_adownsampled'))
    print()
    print("done")  

  print("Saving angular new %s sub-aperture images into %s..." % (indx,(pth_frames+folder+'_'+indx))) 
  if not os.path.exists(pth_frames+folder+'_'+indx):
    os.makedirs(pth_frames+folder+'_'+indx)
  cont = 1
  i = 0
  filenames = []
  for s in range(st_hr):
    auxx = imgs_new[i:(st_hr+i)]
    if s%2 == 0:
      init = 0
      step = 1
      finish = st_hr
    else:
      init = st_hr-1
      step = -1
      finish = -1
      auxx.reverse()
    j = 0  
    for t in range(init, finish, step):
      name = "%s%s_%s/%s_%03d_%02d_%02d.png" % (pth_frames, folder, indx, folder, cont, s+1, t+1)      
      cv2.imwrite(name, auxx[j])
      cont+=1
      j += 1
      filenames.append(name)
      print('.', end="")
    i += st_hr
  print()
  print("done")
  return filenames

def save_frames(files):
  '''
  Function to save sub-aperture images into list in order to pass to video
  constructor
    Input:
      files: list with complete file name of sub-aperture images
    Outputs:
      frame_array: list with the frames
      height: number of rows in frames
      width: number of columns in frames
  '''
  frame_array = []
  for i in files:
    img = cv2.imread(i)
    height, width = img.shape[0:2]
    frame_array.append(img)
  return frame_array, height, width

def write_video(frame_array, name, height, width):
  '''
  Function to invoke a video codec constructor in order to insert frames and
  generate a video with the sub-aperture images
    Inputs:
      frame_array: list with the frames
      name: name of the video to save
      height: number of rows in frames
      width: number of columns in frames
  '''
  #fourcc = cv2.VideoWriter_fourcc(*'XVID') - Linux
  #fourcc = cv2.VideoWriter_fourcc('M','J','P','G') - Windows, avi
  fourcc = cv2.VideoWriter_fourcc(*'mp4v') # MP4
  out = cv2.VideoWriter(name,fourcc, 23.0, (width,height))
  for i in range(len(frame_array)):
    out.write(frame_array[i]) # writing the frame into the codec constructor
  out.release()

# Path withl LF subimages
pth_frames = os.getcwd() + '/LF/Frames/'

f_list = os.listdir(pth_frames)
LRfolders = []
HRfolders = []
for i in f_list:
  if 'adownsampled' in i:
    LRfolders.append(i)            
  elif ('adownsampled' not in i) and ('SRv9' not in i) and ('SRv10' not in i) and ('SRv8' not in i) and ('BC' not in i) and ('NR' not in i) and ('LC' not in i):
    HRfolders.append(i)  
  LRfolders.sort()
  HRfolders.sort()

# Path to save original LF organized by stuv coordinates
pth_LFuvst = os.getcwd() + '/LF/LF_stuv/'

st_hr, st_lr = 10, 5 # original angular resolution, downsampled angular resolution

print("\nLF angular donwsampling: ")
for folder in HRfolders:

  start_time = time.time()
  print("\nProcessing light field %s " % (folder))
  subimgs_list = glob.glob(pth_frames+folder+'/*.png')
  subimgs_list.sort()
  
  #-7
  appnd = [f[-9:] for f in subimgs_list]
  appnd.sort()

  imgshr = []
  for i in appnd:
    for f in subimgs_list:
      #-7
      if i in f[-9:]:
        imghr = cv2.imread(f)
        imgshr.append(imghr)
        h, w, _ = imghr.shape
        break  

  print("Saving original light field structure stuv into %s ..." % ((pth_LFuvst + folder)), end="")
  LFuvst(imgshr, st_hr, pth_LFuvst, folder)
  print('')
  print("done")

  print("Angular downsampling from %d to %d ..." % (st_hr, st_lr), end="")
  ang_mtx, nearest_ang_mtx, bicubic_ang_mtx, lanczos_ang_mtx = AngularDownsampling(imgshr, st_hr, st_lr)
  imgshr = 0
  print('')
  print("done")

  LRsubimgs_list = SynthesizeImgs(ang_mtx, st_lr, h, w, pth_frames, folder, 'adownsampled')
  NRsubimgs_list = SynthesizeImgs(nearest_ang_mtx, st_hr, h, w, pth_frames, folder, 'NR')  
  BCsubimgs_list = SynthesizeImgs(bicubic_ang_mtx, st_hr, h, w, pth_frames, folder, 'BC')
  LCsubimgs_list = SynthesizeImgs(lanczos_ang_mtx, st_hr, h, w, pth_frames, folder, 'LC')
 
  print("Generating video for angular LR light field...")
  frame_array, height, width = save_frames(LRsubimgs_list)
  VD_pth = 'LF/Videos/'
  name = VD_pth + folder + '_adonwsampled.mp4'
  write_video(frame_array, name, height, width)
  print("Video %s has been saved correctly..." % (name))

  print("Generating video for angular HR light field...")
  HRsubimgs_list = glob.glob(pth_frames+folder+'/*.png')
  HRsubimgs_list.sort()
  frame_array, height, width = save_frames(HRsubimgs_list)
  VD_pth = 'LF/Videos/'
  name = VD_pth + folder + '.mp4'
  write_video(frame_array, name, height, width)
  print("Video %s has been saved correctly..." % (name))

  print("Generating video for angular nearest upsampled light field...")
  frame_array, height, width = save_frames(NRsubimgs_list)
  VD_pth = 'LF/Videos/'
  name = VD_pth + folder + '_NR.mp4'
  write_video(frame_array, name, height, width)
  print("Video %s has been saved correctly..." % (name))

  print("Generating video for angular bicubic upsampled light field...")
  frame_array, height, width = save_frames(BCsubimgs_list)
  VD_pth = 'LF/Videos/'
  name = VD_pth + folder + '_BC.mp4'
  write_video(frame_array, name, height, width)
  print("Video %s has been saved correctly..." % (name))

  print("Generating video for angular lanczos upsampled light field...")
  frame_array, height, width = save_frames(LCsubimgs_list)
  VD_pth = 'LF/Videos/'
  name = VD_pth + folder + '_LC.mp4'
  write_video(frame_array, name, height, width)
  print("Video %s has been saved correctly..." % (name))

  print("--- Elapsed time: %s seconds ---" % (time.time() - start_time))

#-----------------------------------------------------------------------------------------------------------------------
# - angular downsampled ando original light field structure uvst synthesizing

# Path withl LF subimages
pth_frames = os.getcwd() + '/LF/Frames/'

f_list = os.listdir(pth_frames)
LRfolders = []
HRfolders = []
for i in f_list:
  if 'adownsampled' in i:
    LRfolders.append(i)            
  elif ('adownsampled' not in i) and ('SRv9' not in i) and ('SRv10' not in i) and ('SRv8' not in i) and ('BC' not in i) and ('NR' not in i) and ('LC' not in i):
    HRfolders.append(i)  
  LRfolders.sort()
  HRfolders.sort()

if len(LRfolders)!=len(HRfolders):
  print("Number of LF are not symetric within different methods of upscaling... Exit program")
  sys.exit("aa! errors!")

def handleimgs(lf_folder):
  imgsfiles = glob.glob(pth_frames+lf_folder+'/*.png')
  imgsfiles.sort()
  return imgsfiles

pth_mosiacos = os.getcwd() + '/LF/LF_uvst/'
print("Saving original and angular donwsampled light field structure uvst into %s ..." % (pth_mosiacos), end="")

startglob_time = time.time()
for LRfolder, HRfolder in zip(LRfolders, HRfolders):

  start_time = time.time()

  print("\nEvaluation of light field %s " % (HRfolder))
  LRsubimgs_list = handleimgs(LRfolder)
  HRsubimgs_list = handleimgs(HRfolder)

  HRimg = cv2.imread(HRsubimgs_list[0])
  HRmosaico = np.zeros((HRimg.shape[0]*10,HRimg.shape[1]*10, 3), np.uint8)

  rowhr = 0
  colhr = 0
  for i in range(len(HRsubimgs_list)):

    HRimg = cv2.imread(HRsubimgs_list[i])

    yi = rowhr*HRimg.shape[1]
    yo = (rowhr*HRimg.shape[1]) + HRimg.shape[1]
    xi = colhr*HRimg.shape[0]
    xo = (colhr*HRimg.shape[0]) + HRimg.shape[0]
    HRmosaico[yi:yo, xi:xo, :] = HRimg
    rowhr += 1
    if rowhr == 10:
      rowhr = 0
      colhr += 1

  print("Saving mosaico images  into %s..." % (pth_mosiacos+HRfolder)) 
  if not os.path.exists(pth_mosiacos+HRfolder):
    os.makedirs(pth_mosiacos+HRfolder)
  hrname = pth_mosiacos + HRfolder + '/' + HRfolder + '_uvst.png'
  cv2.imwrite(hrname, HRmosaico)

  LRimg = cv2.imread(LRsubimgs_list[0])
  LRmosaico = np.zeros((LRimg.shape[0]*5,LRimg.shape[1]*5, 3), np.uint8)
  rowlr = 0
  collr = 0

  for i in range(len(LRsubimgs_list)):

    LRimg = cv2.imread(LRsubimgs_list[i])

    yi = rowlr*LRimg.shape[1]
    yo = (rowlr*LRimg.shape[1]) + LRimg.shape[1]
    xi = collr*LRimg.shape[0]
    xo = (collr*LRimg.shape[0]) + LRimg.shape[0]
    LRmosaico[yi:yo, xi:xo, :] = LRimg
    rowlr += 1
    if rowlr == 5:
      rowlr = 0
      collr += 1

  print("Saving mosaico images  into %s..." % (pth_mosiacos+LRfolder)) 
  if not os.path.exists(pth_mosiacos+LRfolder):
    os.makedirs(pth_mosiacos+LRfolder)
  lrname = pth_mosiacos + LRfolder + '/' + LRfolder + '_uvst.png'
  cv2.imwrite(lrname, LRmosaico)

  print("--- Elapsed time: %s seconds ---" % (time.time() - start_time))

print("--- Elapsed time: %s seconds ---" % (time.time() - startglob_time))


#-------------------------------------------------------------------------------------------------------------------------
# - create h5 dataset for training
import os
import glob
import sys
import cv2
import numpy as np
import time

import h5py
import random

def AngularDownsampling(imgs, st_hr, st_lr):
  dwnfactor = int(st_hr/st_lr)
  # Extract angular matrices for a single spatial point and then downsampling it
  angular_mtcs_hr = []
  angular_mtcs_lr = []
  for u in range(imgs[0].shape[0]):
    print('.', end="")
    for v in range(imgs[0].shape[1]):
      a_mtx = np.zeros((st_hr, st_hr, 3), np.uint8)
      i = 0
      for s in range(st_hr):
        for t in range(st_hr):
          img = imgs[i]
          a_mtx[s, t, :] = img[u, v, :]
          i += 1
      angular_mtcs_hr.append(a_mtx)
      # angular downsampling
      fx = 1/dwnfactor
      fy = 1/dwnfactor
      amtx = cv2.resize(a_mtx, None, fx=fx, fy=fy, interpolation=cv2.INTER_AREA)
      angular_mtcs_lr.append(amtx)
  return angular_mtcs_hr, angular_mtcs_lr

# Path withl LF subimages
pth_frames = os.getcwd() + '/LF/Frames/'

f_list = os.listdir(pth_frames)
LRfolders = []
HRfolders = []
for i in f_list:
  if 'adownsampled' in i:
    LRfolders.append(i)            
  elif ('adownsampled' not in i) and ('SRv9' not in i) and ('SRv10' not in i) and ('SRv8' not in i) and ('BC' not in i) and ('NR' not in i) and ('LC' not in i):
    HRfolders.append(i)  
  LRfolders.sort()
  HRfolders.sort()

# Randomly shuffle list
random.seed(118)
random.shuffle(HRfolders)

# Separate train and validation LFs
aux = int(len(HRfolders)*0.80)
HRfolders_Train = HRfolders[0:aux] # Training dataset by 80% of full dataset
HRfolders_Test = HRfolders[aux:] # Validation dataset by 20% of full dataset

st_hr, st_lr = 10, 5 # original angular resolution, downsampled angular resolution

#fileName = os.getcwd() + '/LF/HDF5_dataset/LF_angular_dataset.h5'
fileName = os.getcwd() + '/LF_angular_dataset_final.h5'

print(len(HRfolders_Train))
print(len(HRfolders_Test))

ang_smpls = 700 * 10 # angular samples to extract from each LF
#ang_smpls = 15 # angular samples to extract from each LF
train_ang_dataset_smpls = len(HRfolders_Train) * ang_smpls # number of angular samples in train dataset
test_ang_dataset_smpls = len(HRfolders_Test) * ang_smpls # number of angular samples in test dataset

print(train_ang_dataset_smpls)
print(test_ang_dataset_smpls)

with h5py.File(fileName, "w") as out:
  out.create_dataset("X_ang_train",(train_ang_dataset_smpls,5,5,3),dtype=np.uint8)
  out.create_dataset("Y_ang_train",(train_ang_dataset_smpls,10,10,3),dtype=np.uint8)      
  out.create_dataset("X_ang_test",(test_ang_dataset_smpls,5,5,3),dtype=np.uint8)
  out.create_dataset("Y_ang_test",(test_ang_dataset_smpls,10,10,3),dtype=np.uint8)      

anglr_train = []
anghr_train = []
for folder in HRfolders_Train:

  start_time = time.time()
  print("\nProcessing light field %s " % (folder))
  subimgs_list = glob.glob(pth_frames+folder+'/*.png')
  subimgs_list.sort()

  appnd = [f[-9:] for f in subimgs_list]
  appnd.sort()

  imgshr = []
  for i in appnd:
    for f in subimgs_list:
      if i in f[-9:]:
        imghr = cv2.imread(f)
        imghr = cv2.cvtColor(imghr,cv2.COLOR_BGR2RGB)
        imgshr.append(imghr)
        break  

  print("Angular downsampling from %d to %d ..." % (st_hr, st_lr), end="")
  mtx_hr, mtx_lr = AngularDownsampling(imgshr, st_hr, st_lr)
  print('')
  print("done")

  if len(mtx_hr) != len(mtx_lr):
    sys.exit("aa! errors! Dataset is not symmetric.. Exit program")

  # Randomly select 'ang_smpls' samples from both hr and lr angular samples
  c = list(zip(mtx_lr, mtx_hr))
  d = random.sample(c, ang_smpls)
  mtx_lr, mtx_hr = zip(*d)

  for i in range(len(mtx_lr)):
    anglr_train.append(mtx_lr[i])
    anghr_train.append(mtx_hr[i])

  print("--- Elapsed time: %s seconds ---" % (time.time() - start_time))

c = list(zip(anglr_train, anghr_train)) # Randomly shuffle both lists in the same order
random.seed(len(anglr_train))
random.shuffle(c)
anglr_train, anghr_train = zip(*c)

def WriteHDF5(samples, dataset):
  k = 0
  with h5py.File(fileName, "a") as out:
    for sample in samples:
      out[dataset][k, ...] = sample
      k+=1

print("\nSaving X_ang_train samples into dataset file...")
WriteHDF5(anglr_train, 'X_ang_train')
print("done")
print("\nSaving Y_ang_train samples into dataset file...")
WriteHDF5(anghr_train, 'Y_ang_train')
print("done")

anglr_test = []
anghr_test = []

for folder in HRfolders_Test:

  start_time = time.time()
  print("\nProcessing light field %s " % (folder))
  subimgs_list = glob.glob(pth_frames+folder+'/*.png')
  subimgs_list.sort()

  appnd = [f[-9:] for f in subimgs_list]
  appnd.sort()

  imgshr = []
  for i in appnd:
    for f in subimgs_list:
      if i in f[-9:]:
        imghr = cv2.imread(f)
        imghr = cv2.cvtColor(imghr,cv2.COLOR_BGR2RGB)
        imgshr.append(imghr)
        break  

  print("Angular downsampling from %d to %d ..." % (st_hr, st_lr), end="")
  mtx_hr, mtx_lr = AngularDownsampling(imgshr, st_hr, st_lr)
  print('')
  print("done")

  if len(mtx_hr) != len(mtx_lr):
    sys.exit("aa! errors! Dataset is not symmetric.. Exit program")
    
  # Randomly select 'ang_smpls' samples from both hr and lr angular samples
  c = list(zip(mtx_lr, mtx_hr))
  d = random.sample(c, ang_smpls)
  mtx_lr, mtx_hr = zip(*d)

  for i in range(len(mtx_lr)):
    anglr_test.append(mtx_lr[i])
    anghr_test.append(mtx_hr[i])

  print("--- Elapsed time: %s seconds ---" % (time.time() - start_time))

c = list(zip(anglr_test, anghr_test)) # Randomly shuffle both lists in the same order
random.seed(len(anglr_test))
random.shuffle(c)
anglr_test, anghr_test = zip(*c)

print("\nSaving X_ang_test samples into dataset file...")
WriteHDF5(anglr_test, 'X_ang_test')
print("done")
print("\nSaving Y_ang_test samples into dataset file...")
WriteHDF5(anghr_test, 'Y_ang_test')
print("done")
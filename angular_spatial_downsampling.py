#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 08:58:46 2021

@author: Felipe Jaramillo
"""
import os
import glob
import sys
import cv2
import numpy as np
import math
from matplotlib import pyplot as plt

def FrequencyFilterin(img, factor):
  h, w = img.shape[:2]
  dft = np.fft.fft2(np.float32(img)) # do dft saving as complex output
  dft_shift = np.fft.fftshift(dft) # apply shift of origin to center of image
  radius = int((1/(2*factor))*h) # create white circle on black background for low pass filter
  mask = np.zeros((h, w, 1), np.float32)
  cy = mask.shape[0] // 2
  cx = mask.shape[1] // 2
  cv2.circle(mask, (cx,cy), radius, 1, -1)
  n = int(h/8)
  if n%2 == 0: n + 1
  mask = cv2.GaussianBlur(mask, (n,n), 0) # antialias mask via blurring
  dft_shift_filtered = np.multiply(dft_shift, mask) # apply mask to dft_shift
  # shift origin from center to upper left corner
  # do idft saving as complex
  # combine complex real and imaginary components to form (the magnitude for) the original image again
  img_flt=(np.abs(np.fft.ifft2(np.fft.ifftshift(dft_shift_filtered))))
  return img_flt

def SpatialDownsampling(img, factor):
  img = np.float32(img) / 255.0 # Normalize image between [0, 1]
  b,g,r = cv2.split(img)
  bflt = FrequencyFilterin(b, factor)
  gflt = FrequencyFilterin(g, factor)
  rflt = FrequencyFilterin(r, factor)
  imgflt = cv2.merge((bflt, gflt, rflt))
  imgdwn = imgflt[::factor, ::factor, :]
  imgdwn = cv2.normalize(imgdwn, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
  return imgdwn

def lcm(a, b):
  return abs(a*b) // math.gcd(a, b)

def AngularDownsampling(imgs, st_hr, st_lr):
  # if downsampling factor is rational or no
  if st_hr%st_lr != 0:
    upfactor = int((lcm(st_hr, st_lr))/st_hr)
    dwnfactor = int((lcm(st_hr, st_lr))/st_lr)
    rat_int = True
  else:
    dwnfactor = int(st_hr/st_lr)
    rat_int = False
  # Extract angular matrices for a single spatial point and then downsampling it
  angular_mtcs = []
  for u in range(imgs[0].shape[0]):
    for v in range(imgs[0].shape[1]):
      a_mtx = np.zeros((st_hr, st_hr, 3), np.uint8)
      i = 0
      print('')
      for s in range(st_hr):
        for t in range(st_hr):
          img = imgs[i]
          a_mtx[s, t, :] = img[u, v, :]
          # angular downsampling
          if rat_int == True:
            amtx = cv2.resize(a_mtx, (0,0), fx=upfactor, fy=upfactor, interpolation=cv2.INTER_CUBIC)
          else:
            amtx = a_mtx
          amtx_dwn = SpatialDownsampling(amtx, dwnfactor)     
          i += 1
          print('.', end="")
      angular_mtcs.append(amtx_dwn)
  return angular_mtcs

def SynthesizeImgs(a_mtxdwn, st_lr, factor, h, w, pth, folder):
  # Once downsampled every angular matrix, we can proceed to sythesize the sub-aperture images
  imgs_new = []
  for s in range(st_lr):
    for t in range(st_lr):
      img = np.zeros((int(h/factor), int(w/factor), 3), np.uint8)
      i = 0
      for u in range(int(h/factor)):
        for v in range(int(w/factor)):
          img[u, v, :] = a_mtxdwn[i][s, t, :]
          i += 1
      #plt.figure()
      #plt.imshow(imglr)
      #plt.show()      
      print('.', end="")
      imgs_new.append(img)
  cont = 1
  i = 0
  for s in range(st_lr):
    auxx = imgs_new[i:(st_lr+i)]
    if s%2 == 0:
      init = 0
      step = 1
      finish = st_lr
    else:
      init = st_lr-1
      step = -1
      finish = -1
      auxx.reverse()
    j = 0  
    for t in range(init, finish, step):
      dec = int(cont/10)
      und = cont%10 
      name = pth + folder + '/' + str(dec) + str(und) + '_' + str(s) + '_' + str(t) + '_' + folder + '.png'
      cv2.imwrite(name, auxx[j])
      cont+=1
      j += 1
      print('.', end="")
    i += st_lr

pth_frames = os.getcwd() + '/LF/Frames/' # Input LF directory
pth_dwn = os.getcwd() + '/LF/Frames_Angular_Spatial_Downsampled/' # Output LF directory

f_list = os.listdir(pth_frames)
LRfolders = []
HRfolders = []

for i in f_list:
  subs = 'downsampled'
  if subs in i: # divide LR and HR folder's names in two list: LRfolders, HRfolders 
    LRfolders.append(i)
  else:
    HRfolders.append(i)
  LRfolders.sort()
  HRfolders.sort()

factor = 2 # spatial downsampling factor
st_hr, st_lr = 9, 5 # original angular resolution, downsampled angular resolution

for folder in HRfolders:

  print("\nProcessing light field %s " % (folder))
  subimgs_list = glob.glob(pth_frames+folder+'/*.png')
  subimgs_list.sort()
  if not os.path.exists(pth_dwn+folder):
    os.makedirs(pth_dwn+folder)

  appnd = [f[-7:] for f in subimgs_list]
  appnd.sort()

  imgs = []
  print("Spatial downsampling by factor of %d " % (factor), end="")
  for i in appnd:
    for f in subimgs_list:
      if i in f[-7:]:
        imghr = cv2.imread(f)
        h, w, _ = imghr.shape
        imglr = SpatialDownsampling(imghr, factor)
        #plt.figure()
        #plt.imshow(imglr)
        #plt.show()
        imgs.append(imglr)
        print('.', end="")
        break
  print()
  print("done")

  print("Angular downsampling from %d to %d " % (st_hr, st_lr), end="")
  a_mtxdwn = AngularDownsampling(imgs, st_hr, st_lr)
  print()
  print("done")

  print("Saving new sub-aperture images into %s " % (pth_dwn+folder), end="")  
  SynthesizeImgs(a_mtxdwn, st_lr, factor, h, w, pth_dwn, folder)
  print()
  print("done")

  #sys.exit("aa! errors!")
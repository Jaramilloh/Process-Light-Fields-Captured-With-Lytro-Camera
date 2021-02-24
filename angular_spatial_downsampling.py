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
import time

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

def AngularDownsampling(imgs, st_hr, st_lr, pth_LFuvst, folder):
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
    print('.', end="")
    for v in range(imgs[0].shape[1]):
      a_mtx = np.zeros((st_hr, st_hr, 3), np.uint8)
      i = 0
      for s in range(st_hr):
        for t in range(st_hr):
          img = imgs[i]
          a_mtx[s, t, :] = img[u, v, :]
          i += 1
      # angular downsampling
      #if rat_int == True:
        #amtx = cv2.resize(a_mtx, (0,0), fx=upfactor, fy=upfactor, interpolation=cv2.INTER_CUBIC)
      #else:
        #amtx = a_mtx
      #amtx_dwn = SpatialDownsampling(amtx, dwnfactor)
      amtx_dwn = a_mtx[::2, ::2, :]
      angular_mtcs.append(amtx_dwn)
  return angular_mtcs

def SynthesizeImgs(a_mtxdwn, st_lr, factor, h, w, pth_frames, pth_LFuvst, folder):  
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

  print("Saving angular spatial downsampled light field structure stuv into %s " % ((pth_LFuvst+folder+'_asdownsampled')), end="")
  LFuvst(imgs_new, st_lr, pth_LFuvst, (folder+'_asdownsampled'))
  print()
  print("done")  

  print("Saving new sub-aperture images into %s " % ((pth_frames+folder+'_asdownsampled...'))) 
  if not os.path.exists(pth_frames+folder+'_asdownsampled'):
    os.makedirs(pth_frames+folder+'_asdownsampled')
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
      name = pth_frames + folder + '_asdownsampled' + '/' + folder + '_' + str(dec) + str(und) + '_' + str(s+1) + '_' + str(t+1) + '.png'
      cv2.imwrite(name, auxx[j])
      cont+=1
      j += 1
      print('.', end="")
    i += st_lr
  print()
  print("done")  


# Path withl LF subimages
pth_frames = os.getcwd() + '/LF/Frames/'
# Path to save original LF organized by stuv coordinates
pth_LFuvst = os.getcwd() + '/LF/LF_stuv/'

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

  start_time = time.time()
  print("\nProcessing light field %s " % (folder))
  subimgs_list = glob.glob(pth_frames+folder+'/*.png')
  subimgs_list.sort()

  appnd = [f[-7:] for f in subimgs_list]
  appnd.sort()

  print("Spatial downsampling by factor of %d " % (factor))
  imgshr = []
  imgslr = []
  if not os.path.exists(pth_frames+folder+'_sdownsampled'):
    os.makedirs(pth_frames+folder+'_sdownsampled')
  print("Saving results at %s " % ((pth_frames+folder+'_sdownsampled')), end="") 
  for i in appnd:
    for f in subimgs_list:
      if i in f[-7:]:
        imghr = cv2.imread(f)
        imgshr.append(imghr)
        h, w, _ = imghr.shape
        imglr = SpatialDownsampling(imghr, factor)
        name = pth_frames+folder+'_sdownsampled/' + f[-19:]
        cv2.imwrite(name, imglr)
        #plt.figure()
        #plt.imshow(imglr)
        #plt.show()
        imgslr.append(imglr)
        print('.', end="")
        break  
  print()
  print("done")

  print("Saving original light field structure stuv into %s ..." % ((pth_LFuvst + folder)), end="")
  LFuvst(imgshr, st_hr, pth_LFuvst, folder)
  imgshr = 0
  print('')
  print("done")

  print("Angular downsampling from %d to %d ..." % (st_hr, st_lr), end="")
  a_mtxdwn = AngularDownsampling(imgslr, st_hr, st_lr, pth_LFuvst, folder)
  imgslr = 0
  print('')
  print("done")

  print("Saving new sub-aperture images into %s " % (pth_frames+folder+'_downsampled...'), end="")  
  SynthesizeImgs(a_mtxdwn, st_lr, factor, h, w, pth_frames, pth_LFuvst, folder)
  print()
  print("done")

  print("--- Elapsed time: %s seconds ---" % (time.time() - start_time))
  #sys.exit("aa! errors!")
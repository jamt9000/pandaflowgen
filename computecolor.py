import numpy as np

def computeColor(u,v):
    
    #   computeColor color codes flow field U, V

    # To Python by James Thewlis
    
    #   According to the c++ source code of Daniel Scharstein 
    #   Contact: schar@middlebury.edu
    
    #   Author: Deqing Sun, Department of Computer Science, Brown University
    #   Contact: dqsun@cs.brown.edu
    #   $Date: 2007-10-31 21:20:30 (Wed, 31 Oct 2006) $
    
    # Copyright 2007, Deqing Sun.
    #
    #                         All Rights Reserved
    #
    # Permission to use, copy, modify, and distribute this software and its
    # documentation for any purpose other than its incorporation into a
    # commercial product is hereby granted without fee, provided that the
    # above copyright notice appear in all copies and that both that
    # copyright notice and this permission notice appear in supporting
    # documentation, and that the name of the author and Brown University not be used in
    # advertising or publicity pertaining to distribution of the software
    # without specific, written prior permission.
    #
    # THE AUTHOR AND BROWN UNIVERSITY DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
    # INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR ANY
    # PARTICULAR PURPOSE.  IN NO EVENT SHALL THE AUTHOR OR BROWN UNIVERSITY BE LIABLE FOR
    # ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    # WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    # ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    # OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE. 
    
    nanIdx = np.isnan(u) | np.isnan(v);
    u[nanIdx] = 0;
    v[nanIdx] = 0;
    
    colorwheel = makeColorwheel();
    ncols = colorwheel.shape[0]
    
    rad = np.sqrt(u**2+v**2);          
    
    a = np.arctan2(-v,-u)/np.pi;
    
    fk = ((a+1) /2).dot(ncols-1) + 1;  # -1~1 maped to 1~ncols
       
    k0 = np.int_(np.floor(fk));                 # 1, 2, ..., ncols
    
    k1 = k0+1;
    k1[k1==ncols+1] = 1;
    
    f = fk - k0;
    img = np.uint8(np.zeros((u.shape[0],u.shape[1],3)))
    #print k0.shape
    
    for i in range(0,colorwheel.shape[1]):
        tmp = colorwheel[:,i];
        col0 = tmp[k0-1]/255;
        col1 = tmp[k1-1]/255;
        col = (1-f)*col0 + f*col1;   
       
        idx = rad <= 1;   
        col[idx] = 1-rad[idx]*(1-col[idx]);    # increase saturation with radius
        
        col[~idx] = col[~idx]*0.75;             # out of range
        
        img[:,:,i] = np.uint8(np.floor(255*col*(1-nanIdx)));           
    return img
    
    ##
def makeColorwheel():
    
    #   color encoding scheme
    
    #   adapted from the color circle idea described at
    #   http://members.shaw.ca/quadibloc/other/colint.htm
    
    
    RY = 15;
    YG = 6;
    GC = 4;
    CB = 11;
    BM = 13;
    MR = 6;
    
    ncols = RY + YG + GC + CB + BM + MR;
    
    colorwheel = np.zeros([ncols, 3]); # r g b
    
    col = 0;
    #RY
    colorwheel[0:RY, 0] = 255;
    colorwheel[0:RY, 1] = np.floor(255*(np.arange(0,RY))/RY).T;
    col = col+RY;
    
    #YG
    colorwheel[col:col+YG, 0] = 255 - np.floor(255*(np.arange(0,YG))/YG).T;
    colorwheel[col:col+YG, 1] = 255;
    col = col+YG;

    #GC
    colorwheel[col:col+GC, 1] = 255;
    colorwheel[col:col+GC, 2] = np.floor(255*(np.arange(0,GC))/GC).T;
    col = col+GC;
    
    #CB
    colorwheel[col:col+CB, 1] = 255 - np.floor(255*(np.arange(0,CB))/CB).T;
    colorwheel[col:col+CB, 2] = 255;
    col = col+CB;
    
    #BM
    colorwheel[col:col+BM, 2] = 255;
    colorwheel[col:col+BM, 0] = np.floor(255*(np.arange(0,BM))/BM).T;
    col = col+BM;
    
    #MR
    colorwheel[col:col+MR, 2] = 255 - np.floor(255*(np.arange(0,MR))/MR).T;
    colorwheel[col:col+MR, 0] = 255;
    return colorwheel

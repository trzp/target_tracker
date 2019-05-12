#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/3 14:42
# @Version : 1.0
# @File    : kcftracker_mul_pro.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved


import kcftracker
from pykinect import KinectClientV2019
from pykinect import locate_obj
from pykinect import locate_bottle
import multiprocessing
from multiprocessing import Queue, Event
import time


def tracker_pro(args):
    ev = args['ev']
    quin = args['quin']
    quout = args['quout']
    tracker = kcftracker.KCFTracker(True, True, True)
    kk = KinectClientV2019()
    
    while not ev.is_set():
        flg, box = quin.get()
        if flg == 1:  # 启动跟踪
            frame = kk.get_color_as_cvframe()
            tracker.init(box, frame)

        elif flg == 2:  # 请求结果
            frame = kk.get_color_as_cvframe()
            boundingbox = tracker.update(frame)
            x, y, w, h = boundingbox = map(int, boundingbox)
            pos = locate_obj(((x, y), (w, h)), kk.point_cloud)
            pos1 = locate_bottle(((x, y), (w, h)), kk.point_cloud)
            quout.put([boundingbox, {'obj': pos, 'bottle': pos1}])

        elif flg == 0:
            pass
            
class TrackerPro():
    def __init__(self):
        self.ev = Event()
        self.quout = Queue()
        self.quin = Queue()
        self.args = {'ev':self.ev,'quin':self.quout,'quout':self.quin}
    
    def init_tracker(self,box): #box: x,y,w,h 
        self.quout.put([1,box])
    
    def update(self):
        self.quout.put([2,None])
        return self.quin.get()

if __name__ == '__main__':
    tracker = TrackerPro()
    process = multiprocessing.Process(target = tracker_pro,args = (tracker.args))
    process.start()
    
    tracker.init()
    while True:
        r = tracker.update()


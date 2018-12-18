#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import random
import tensorflow as tf
import matplotlib.pyplot as plt
import scipy.misc
import os
import csv
import itertools
import tensorflow.contrib.slim as slim
from PIL import Image
from PIL import ImageDraw 
from PIL import ImageFont
from math import floor
from graphviz import Digraph

# Copies one set of variables to another.
# Used to set worker network parameters to those of global network.
def update_target_graph(from_scope,to_scope):
    from_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, from_scope)
    to_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, to_scope)

    op_holder = []
    for from_var,to_var in zip(from_vars,to_vars):
        op_holder.append(to_var.assign(from_var))
    return op_holder

# Discounting function used to calculate discounted returns.
def discount(x, gamma):
    return scipy.signal.lfilter([1], [1, -gamma], x[::-1], axis=0)[::-1]

#Used to initialize weights for policy and value output layers
def normalized_columns_initializer(std=1.0):
    def _initializer(shape, dtype=None, partition_info=None):
        out = np.random.randn(*shape).astype(np.float32)
        out *= std / np.sqrt(np.square(out).sum(axis=0, keepdims=True))
        return tf.constant(out)
    return _initializer


#This code allows gifs to be saved of the training episode for use in the Control Center.
def make_gif(filenames, fname, duration=1):
  import moviepy.editor as mpy
  import imageio
  
  images = []
  for filename in filenames:
    images.append(imageio.imread(filename))
  imageio.mimsave(fname, images, duration=duration)

  #clean the folder
  for filename in filenames:
    # delete frame
    os.remove(filename)
    #delete c file generated by graphviz
    c_filename = filename.split(".png")[0]
    os.remove(c_filename)

# def set_image_bandit(values,probs,selection,trial):
def make_frame(save_path, t_list, r_list, trial, action=-1, final_state=-1, reward=-1): 
#     r = 0.9
#     r_list=[r,1-r] 
#     action=0
#     final_state=1
#     reward=1

    dot = Digraph(comment='DecisionTree')

    s_colors=["white"]*2
    if final_state > -1:
        s_colors[final_state-1]="lightblue2"

    reward_color = ["white"]*2
    if reward == 0:
        reward_color[0] = "red"
    elif reward == 1:
        reward_color[1] = "green"
    
        
        
    r_colors = ["black"]*4
    dot.node('S1')
    dot.node('S2', fillcolor=s_colors[0], style="filled")
    dot.node('S3', fillcolor=s_colors[1], style="filled")

    dot.node('R1','1', fillcolor=reward_color[1], style="filled")
    dot.node('R0','0', fillcolor=reward_color[0], style="filled")
    


    dot.node('A1', '', shape='square', width='0.1')
    dot.node('A2', '', shape='square', width='0.1')
    
    dot.node('T', 'Trial :'+str(int(trial/2)),width='0.1')

    a_colors=["black"]*2
    fs_colors=["black"]*4
    r_colors=["black"]*4

    if action >= 0:
        a_colors[action] = "green"
    if final_state > 0:
        if t_list[action][final_state-1]>=0.5:
            color = "blue"
        else:
            color = "red"
        fs_colors[action+(final_state-1)*2] = color
    if reward > -1 :
        if r_list[final_state-1, 1-reward] >= 0.5:
            color = "blue"
        else:
            color = "red"
        r_colors[(final_state-1)*2+reward]= color



    dot.edge('S1', 'A1', label="a1", color=a_colors[0])
    dot.edge('S1', 'A2', label="a2", color=a_colors[1])
    dot.edge('A1', 'S2', label=str(round((t_list[0][0])*100))+"%", style="bold", dir="none", color=fs_colors[0])
    dot.edge('A1', 'S3', label=str(round((t_list[0][1])*100))+"%", dir="none", color=fs_colors[2])
    dot.edge('A2', 'S2', label=str(round((t_list[1][0])*100))+"%", dir="none", color=fs_colors[1])
    dot.edge('A2', 'S3', label=str(round((t_list[1][1])*100))+"%", style="bold", dir="none", color=fs_colors[3])

    dot.edge('S2', 'R1', label=str(round(r_list[0][0]*100))+"%", dir="none", color=r_colors[1])
    dot.edge('S2', 'R0', label=str(round((r_list[0][1])*100))+"%", dir="none", color=r_colors[0])
    
    dot.edge('S3', 'R1', label=str(round(r_list[1][0]*100))+"%", dir="none", color=r_colors[3])
    dot.edge('S3', 'R0', label=str(round((r_list[1][1])*100))+"%", dir="none", color=r_colors[2])
    
    dot.format='png'
    title = save_path+"/trial_"+str(trial)
    dot.render(title)
    #print("saved ",title)
    dot
    return title+".png"
    
    
    
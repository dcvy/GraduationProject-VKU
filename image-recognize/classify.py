import tkinter as tk
from tkinter import filedialog
from fastai.vision.all import *
import numpy as np
import sys
import os
import pathlib

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

labels = pd.read_csv('D:/codes/python/image_main/input/clothing-dataset-full/images.csv')
labels['label'].value_counts()
labels.loc[labels['label'] == 'Not sure', 'label'] = 'Not_sure'
labels['image'] = labels['image'] + '.jpg'
labels['label_cat'] = labels['label'] + ' ' + labels['kids'].astype(str)
label_df = labels[['image', 'label_cat']]
path = 'D:/codes/python/image_main/input/clothing-dataset-full'


def get_x(r): return path+'/images_original/'+r['image']
def get_y(r): return r['label_cat'].split(' ')

dblock = DataBlock(blocks=(ImageBlock, MultiCategoryBlock),
                   get_x=get_x, get_y=get_y,
                   item_tfms=RandomResizedCrop(128, min_scale=0.35))
dls = dblock.dataloaders(label_df)
dls.show_batch(nrows=3, ncols=3)

learn = load_learner('D:/codes/python/image_main/output/export2.pkl')

if __name__ == '__main__':
    def classify_image(file_path):
        img = Image.open(file_path)
        img.thumbnail((128, 128))
        img = TensorImage(array(img)).permute(2, 0, 1)  # Convert to Fastai Image
        pred, pred_idx, probs = learn.predict(img)

        highest_score_idx = np.argmax(probs)
        highest_score_label = learn.dls.vocab[highest_score_idx]
        highest_score = probs[highest_score_idx]

        pred0 = pred[0]
        pred1 = pred[1]
        if pred0 == 'False':
            result = f'{pred1} (score = {highest_score:.5f})'
        else:
            result = f'{pred1} (score = {highest_score:.5f})'
        
        return result

    # Check if a file path is provided as a command-line argument
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        result = classify_image(file_path)
        print(result)
    else:
        print("Please provide a valid image file path as a command-line argument.")

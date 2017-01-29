from stl_tools import numpy2stl

import json
import urllib
import boto3

from scipy.misc import imresize
from scipy.ndimage import gaussian_filter
from pylab import imread

client = boto3.client('sqs')


def MakeSTL():
    key = PurseSQS();
    s3 = boto3.resource('s3')
    s3.Object('smart-3d', key).download_file(key)
    A = 256 * imread(key)
    A = A[:, :, 2] + 1.0*A[:,:, 0] # Compose RGBA channels to give depth
    A = gaussian_filter(A, 1)  # smoothing
    numpy2stl(A, 'examples.stl', scale=0.05, mask_val=5., solid=True)
    s3.meta.client.upload_file('examples.stl', 'smart-3d', 'examples.stl')

def PurseSQS():
    sqs = boto3.resource('sqs')
    que_message = client.receive_message(
        QueueUrl = 'https://sqs.ap-northeast-1.amazonaws.com/743424264703/Image'
)
    if "Messages" in que_message:
        records = que_message['Messages'][0]['Body']
        print records
        start = records.rindex('key')
        end = records.rindex('png')
        print records[start+6:end+3]
        key = records[start+6:end+3]
        key = key.replace('+',' ')
    else:
        print 'Wrong Queue, That is it'
   
    return key

# while 1
MakeSTL();

from stl_tools import numpy2stl

import json
import urllib
import boto3

#from scipy.misc import imresize
from scipy.ndimage import gaussian_filter
from pylab import imread

client = boto3.client('sqs')

while 1:
    que_message = client.receive_message(
        QueueUrl = 'yourQueueUrl'
)
    if "Messages" in que_message:
        records = que_message['Messages'][0]['Body']
        head = records.rindex('key')
        print records
        if 'png' in records:
            tail = records.rindex('png')
            key = records[head+6:tail+3].replace('+',' ')
        elif 'jpg' in records:
            tail = records.rindex('jpg')
            key = records[head+6:tail+3].replace('+',' ')
        else:
            print "wrong queue"
            break;
        s3 = boto3.resource('s3')
        s3.Object('your-bucketname', key).download_file(key)
        A = 256 * imread(key)
        A = A[:, :, 2] + 1.0*A[:,:, 0] # Compose RGBA channels to give depth
        A = gaussian_filter(A, 1)  # smoothing
        numpy2stl(A, 'examples.stl', scale=0.05, mask_val=5., solid=True)
        s3.meta.client.upload_file('examples.stl', 'yourbucket-name', 'examples.stl')
        client.delete_message(
            QueueUrl = 'your-QueurUrl',
            ReceiptHandle = que_message["Messages"][0]["ReceiptHandle"]
                )
        print "successfully uploaded!"
    else:
        print 'None of queue'

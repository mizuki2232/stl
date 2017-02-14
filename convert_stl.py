from stl_tools import numpy2stl

import json
import urllib
import boto3

from scipy.misc import imresize
from scipy.ndimage import gaussian_filter
from pylab import imread

client = boto3.client('sqs')

while 1:
    que_message = client.receive_message(
        QueueUrl = 'https://sqs.ap-northeast-1.amazonaws.com/743424264703/Image'
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
        s3.Object('smart-3d', key).download_file(key)
        A = 256 * imread(key)
        A = A[:, :, 2] + 1.0*A[:,:, 0] # Compose RGBA channels to give depth
        A = gaussian_filter(A, 1)  # smoothing
        numpy2stl(A, 'examples.stl', scale=0.05, mask_val=5., solid=True)
        s3.meta.client.upload_file('examples.stl', 'smart-3d', 'examples.stl')
        entries = []
        maxNumberOfMessages = 10
        queue = boto3.resource('sqs').get_queue_by_name(
                QueueName = "Image"
        )
        messages = queue.receive_messages(
            MaxNumberOfMessages = maxNumberOfMessages
                    )
        for message in messages:
            entries.append({
                "Id": message.message_id,
                "ReceiptHandle": message.receipt_handle
            })
        queue.delete_messages(
                Entries = entries
            )
    else:
        print 'None of queue'


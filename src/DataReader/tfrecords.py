import tensorflow as tf
import os
from PIL import Image
class TFRecords_Reader(object):
    def __init__(self):
        self.__num_examples = 0

    def write_records(self, img_dir, label_dir, records_name):
        writer = tf.python_io.TFRecordWriter(records_name)
        for name in os.listdir(img_dir):
            img_path = os.path.join(img_dir, name)
            img = Image.open(img_path,'r')
            img_raw = img.tobytes()
            label_path = os.path.join(label_dir, name)
            label = Image.open(label_path,'r').split()
            label_raw = label[0].tobytes()
            example = tf.train.Example(features=tf.train.Features(feature={
                "index" : tf.train.Feature(float_list=tf.train.FloatList(value=[name])),
                "img_row" : tf.train.Feature(bytes_list=tf.train.BytesList(value=[img_raw])),
                "annot_img_row" : tf.train.Feature(bytes_list=tf.train.BytesList(value=[label_raw]))
            }))
            writer.write(example.SerializeToString())
            self.__num_examples += 1
            print(name)
        print('num examples : ', self.__num_examples )
        writer.close()

    def readbatch_by_queue(self, records_name, batch_size, num_epoch):
        filename_queue = tf.train.string_input_producer([records_name], num_epoch)
        reader = tf.TFRecordReader()
        _, serialized_example = reader.read(filename_queue)
        features = tf.parse_single_example(serialized_example,
                                           features={
                                               "index" : tf.FixedLenFeature([], tf.float32),
                                               "img_row" : tf.FixedLenFeature([], tf.string),
                                               "annot_img_row" : tf.FixedLenFeature([], tf.string)
                                           })
        index = features["index"]
        img = tf.decode_raw(features["img_row"], tf.uint8)
        img = tf.reshape(img, [300, 400, 3])
        img = tf.cast(img, tf.float32)
        annot_img = tf.decode_raw(features["annot_img_row"], tf.uint8)
        annot_img = tf.reshape(annot_img, [300, 400, 1])
        annot_img = tf.cast(annot_img, tf.float32)
        min_after_dequeue = 100
        capacity = min_after_dequeue + 3 * batch_size
        index_batch, img_batch, annot_img_batch = tf.train.shuffle_batch(
            [index, img, annot_img], batch_size=batch_size,
            capacity=capacity, min_after_dequeue=min_after_dequeue)
        return index_batch, img_batch, annot_img_batch

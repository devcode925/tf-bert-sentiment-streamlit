import os
import shutil

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
from official.nlp import optimization  # to create AdamW optmizer

import matplotlib.pyplot as plt

tf.get_logger().setLevel('ERROR')
class BertSentiment:
    def __init__(self, name ):
        self.name = name

    def buildModel(self):
        url = 'https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz'

        dataset = tf.keras.utils.get_file('aclImdb_v1.tar.gz', url,
                                      untar=True, cache_dir='.',
                                      cache_subdir='')

        dataset_dir = os.path.join(os.path.dirname(dataset), 'aclImdb')

        train_dir = os.path.join(dataset_dir, 'train')

        # remove unused folders to make it easier to load the data
        remove_dir = os.path.join(train_dir, 'unsup')
        shutil.rmtree(remove_dir)

        AUTOTUNE = tf.data.AUTOTUNE
        batch_size = 32
        seed = 42

        raw_train_ds = tf.keras.preprocessing.text_dataset_from_directory(
            'aclImdb/train',
            batch_size=batch_size,
            validation_split=0.2,
            subset='training',
            seed=seed)

        class_names = raw_train_ds.class_names
        train_ds = raw_train_ds.cache().prefetch(buffer_size=AUTOTUNE)

        val_ds = tf.keras.preprocessing.text_dataset_from_directory(
            'aclImdb/train',
            batch_size=batch_size,
            validation_split=0.2,
            subset='validation',
            seed=seed)

        val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

        test_ds = tf.keras.preprocessing.text_dataset_from_directory(
            'aclImdb/test',
            batch_size=batch_size)

        test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)

        bert_model_name = 'small_bert/bert_en_uncased_L-4_H-512_A-8'

        map_name_to_handle = {
            'bert_en_uncased_L-12_H-768_A-12':
                'https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/3',
            'small_bert/bert_en_uncased_L-4_H-512_A-8':
                'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1',
            'small_bert/bert_en_uncased_L-4_H-768_A-12':
                'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-768_A-12/1',
            'small_bert/bert_en_uncased_L-12_H-768_A-12':
                'https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-12_H-768_A-12/1',
            'albert_en_base':
                'https://tfhub.dev/tensorflow/albert_en_base/2',
            'electra_small':
                'https://tfhub.dev/google/electra_small/2',
            'electra_base':
                'https://tfhub.dev/google/electra_base/2',
            'experts_pubmed':
                'https://tfhub.dev/google/experts/bert/pubmed/2',
            'experts_wiki_books':
                'https://tfhub.dev/google/experts/bert/wiki_books/2',
            'talking-heads_base':
                'https://tfhub.dev/tensorflow/talkheads_ggelu_bert_en_base/1',
        }

        map_model_to_preprocess = {
            'bert_en_uncased_L-12_H-768_A-12':
                'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',            
            'small_bert/bert_en_uncased_L-4_H-512_A-8':
                'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
            'small_bert/bert_en_uncased_L-4_H-768_A-12':
                'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',            
            'albert_en_base':
                'https://tfhub.dev/tensorflow/albert_en_preprocess/3',
            'electra_small':
                'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
            'electra_base':
                'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
            'experts_pubmed':
                'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
            'experts_wiki_books':
                'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
            'talking-heads_base':
                'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3',
        }

        tfhub_handle_encoder = map_name_to_handle[bert_model_name]
        tfhub_handle_preprocess = map_model_to_preprocess[bert_model_name]

        print(f'BERT model selected           : {tfhub_handle_encoder}')
        print(f'Preprocess model auto-selected: {tfhub_handle_preprocess}')

        bert_preprocess_model = hub.KerasLayer(tfhub_handle_preprocess)

        text_test = ['this is such an amazing movie!']
        text_preprocessed = bert_preprocess_model(text_test)

        print(f'Keys       : {list(text_preprocessed.keys())}')
        # print(f'Shape      : {text_preprocessed[input_word_ids].shape}')
        # print(f'Word Ids   : {text_preprocessed[input_word_ids][0, :12]}')
        # print(f'Input Mask : {text_preprocessed[input_mask][0, :12]}')
        # print(f'Type Ids   : {text_preprocessed[input_type_ids][0, :12]}')

        bert_model = hub.KerasLayer(tfhub_handle_encoder)

        bert_results = bert_model(text_preprocessed)

        print(f'Loaded BERT: {tfhub_handle_encoder}')

    
        classifier_model = build_classifier_model()
        bert_raw_result = classifier_model(tf.constant(text_test))
        print(tf.sigmoid(bert_raw_result))

        loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)
        metrics = tf.metrics.BinaryAccuracy()

        epochs = 5
        steps_per_epoch = tf.data.experimental.cardinality(train_ds).numpy()
        num_train_steps = steps_per_epoch * epochs
        num_warmup_steps = int(0.1 * num_train_steps)

        init_lr = 3e-5
        optimizer = optimization.create_optimizer(init_lr=init_lr,
                                              num_train_steps=num_train_steps,
                                              num_warmup_steps=num_warmup_steps,
                                              optimizer_type='adamw')

        classifier_model.compile(optimizer=optimizer,
                             loss=loss,
                             metrics=metrics)

        print(f'Training model with {tfhub_handle_encoder}')
        history = classifier_model.fit(x=train_ds,
                                   validation_data=val_ds,
                                   epochs=epochs)

        loss, accuracy = classifier_model.evaluate(test_ds)

        print(f'Loss: {loss}')
        print(f'Accuracy: {accuracy}')

        dataset_name = 'imdb'
        saved_model_path = './{}_bert'.format(dataset_name.replace('/', '_'))

        classifier_model.save(saved_model_path, include_optimizer=False)

        reloaded_model = tf.saved_model.load(saved_model_path)
        examples = [
            'this is such an amazing movie!',  # this is the same sentence tried earlier
            'The movie was great!',
            'The movie was meh.',
            'The movie was okish.',
            'The movie was terrible...'
        ]

        reloaded_results = tf.sigmoid(reloaded_model(tf.constant(examples)))
        original_results = tf.sigmoid(classifier_model(tf.constant(examples)))

        print('Results from the saved model:')
        print_my_examples(examples, reloaded_results)
        print('Results from the model in memory:')
        print_my_examples(examples, original_results)
        print(f'Model built and saved to {saved_model_path}')

        # print(f'Pooled Outputs Shape:{bert_results[pooled_output].shape}')
        # print(f'Pooled Outputs Values:{bert_results[pooled_output][0, :12]}')
        # print(f'Sequence Outputs Shape:{bert_results[sequence_output].shape}')
        # print(f'Sequence Outputs Values:{bert_results[sequence_output][0, :12]}')

    def build_classifier_model():
        text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
        preprocessing_layer = hub.KerasLayer(tfhub_handle_preprocess, name='preprocessing')
        encoder_inputs = preprocessing_layer(text_input)
        encoder = hub.KerasLayer(tfhub_handle_encoder, trainable=True, name='BERT_encoder')
        outputs = encoder(encoder_inputs)
        net = outputs['pooled_output']
        net = tf.keras.layers.Dropout(0.1)(net)
        net = tf.keras.layers.Dense(1, activation=None, name='classifier')(net)
        return tf.keras.Model(text_input, net)
    
    @staticmethod
    def print_my_examples(inputs, results):
        result_for_printing = [f'input: {inputs[i]:<30} : score: {results[i][0]:.6f}'
                           for i in range(len(inputs))]
        print(*result_for_printing, sep='\n')
        print()

    @classmethod
    def predict(cls, text):
        dataset_name ='imdb'
        saved_model_path = './{}_bert'.format(dataset_name.replace('/', '_'))
        reloaded_model = tf.saved_model.load(saved_model_path)
        oneList = [text]
        reloaded_results = tf.sigmoid(reloaded_model(tf.constant(oneList)))
        cls.print_my_examples(oneList, reloaded_results)
        return "{:.2f}".format(reloaded_results[0][0])

    if __name__ == '__main__':
        # predict('We think we are happy')
        print('main')

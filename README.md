# tf-bert-sentiment-streamlit
sentiment analysis using bert and streamlit

Inspects the given text and identifies the prevailing emotional opinion within the text, especially to determine a writer\'s attitude as positive, or negative.
"100" is a perfect Positive score. 50 would be consider neutral.

The base machine learning model is Google\'s small_bert/bert_en_uncased_L-4_H-512_A-8. Bert info( https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1 https://huggingface.co/bert-base-uncased)
We trained the model on the Large Movie dataset, cited below.
The core dataset contains 50,000 reviews split evenly into 25k train and 25k test sets.


    
Cite: @InProceedings{maas-EtAl:2011:ACL-HLT2011,
author    = {Maas, Andrew L.  and  Daly, Raymond E.  and  Pham, Peter T.  and  Huang,
     Dan and Ng, Andrew Y. and  Potts, Christopher},
title     = {Learning Word Vectors for Sentiment Analysis},
booktitle = {Proceedings of the 49th Annual Meeting of the Association for 
     Computational Linguistics: Human Language Technologies},
month     = {June},
year      = {2011},
address   = {Portland, Oregon, USA},
publisher = {Association for Computational Linguistics},
pages     = {142--150},')
url       = {http://www.aclweb.org/anthology/P11-1015}
}

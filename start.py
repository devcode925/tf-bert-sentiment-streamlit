from bert_sentiment import BertSentiment
import streamlit as st
import pandas as pd
from io import StringIO

st.write('Inspects the given text and identifies the prevailing emotional opinion within the text, especially to determine a writer\'s attitude as positive, or negative.')
st.write('\"100\" is a perfect Positive score. 50 would be consider neutral.')


st.title('Sentiment Analysis')

st.write('The base machine learning model is Google\'s small_bert/bert_en_uncased_L-4_H-512_A-8.')
st.write('We trained the model on the Large Movie dataset, cited below.')
st.write('The core dataset contains 50,000 reviews split evenly into 25k train and 25k test sets.')


text_to_analysis = st.text_input('Enter your text here')

model = BertSentiment('bert')

if st.button('Get the Score'):
    generated_text = model.predict(text_to_analysis)
    float_str = float(generated_text)
    float_str *= 100
    fixed = int(float_str)
    st.write('Your score: ' +str(fixed))    
    st.write("Your Postivity Score is on the left. A negative score of 20 is shown on the right, for comparsion.")
    with st.beta_container():        
        st.bar_chart({"Score": [fixed, 20]})

    
    
    
st.text('Cite: @InProceedings{maas-EtAl:2011:ACL-HLT2011,')
st.text('  author    = {Maas, Andrew L.  and  Daly, Raymond E.  and  Pham, Peter T.  and  Huang,')
st.text('        Dan and Ng, Andrew Y. and  Potts, Christopher},')
st.text('  title     = {Learning Word Vectors for Sentiment Analysis},')
st.text('  booktitle = {Proceedings of the 49th Annual Meeting of the Association for ')
st.text('        Computational Linguistics: Human Language Technologies},')
st.text('  month     = {June},')
st.text('  year      = {2011},')
st.text('  address   = {Portland, Oregon, USA},')
st.text('  publisher = {Association for Computational Linguistics},')
st.text('  pages     = {142--150},')
st.text('  url       = {http://www.aclweb.org/anthology/P11-1015}')
st.text('}')
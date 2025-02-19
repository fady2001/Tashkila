# coding: utf-8

# In[ ]:


DATASET_FOLDER = 'dataset'
CLEAN_OUT_FOLDER = 'clean_out'
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# In[11]:


# read dataset train 
def read_dataset(file_name = 'train.txt' ,verbose=False):
    """
    takes a file name and returns a pandas dataframe of the dataset 
    the returnes is a pandas series of the dataset 
    """
    
    dataset = os.path.join(DATASET_FOLDER, file_name)
    # read dataset as a text file and each line as a training example
    dataset = pd.read_csv(dataset, sep='\t', header=None).squeeze('columns')
    
    if verbose:
        print('dataset shape: ', dataset.shape)
        print('first 5 examples: ')
        print(dataset[:5])
    
    return dataset

read_dataset(verbose=True);


# In[ ]:






# In[12]:


text = 'تَغْتَرَّ'
print(len(text))

# shadda and other diacritics are single characters
for i in range(len(text)):
    print(text[i], ord(text[i]))
    
print('--------------------')

print("يّيلعبُُُ")


# In[13]:


# geet all the tashkeel in the text 
from constants import ARABIC_LETTERS 
All_NON_Letters = set()
for text in read_dataset():
    for c in text:
        if c not in ARABIC_LETTERS:
            All_NON_Letters.add(c)
            
print(All_NON_Letters)


# In[14]:


from constants.arabic import HARAKAT
from constants import PUNCTUATIONS
from constants.arabic import ARABIC_NUMBERS

import re
from constants.arabic import ARABIC_NUMBERS
from constants import PUNCTUATIONS
# Compile regular expressions
number_regex = re.compile(r'[0-9]')
arabic_number_regex = re.compile(r'[' + "".join(ARABIC_NUMBERS) + ']')
punctuation_regex = re.compile(r'[' + "".join(PUNCTUATIONS) + ']')
spaces_regex = re.compile(r'\s+')

def clean_text(text):
    # Delete all numbers and punctuation
    # Remove numbers
    text = number_regex.sub('', text)
    text = arabic_number_regex.sub('', text)
    # Remove punctuation marks
    # text = punctuation_regex.sub('', text)
    # Compress all spaces
    text = spaces_regex.sub(' ', text)
    
    text = text.strip()
    
    return text

text = '0110ز؟:.+_@#$.زتَغْتَرَّ2//،،312)()( جداى آيئءؤرلاىةوزظلآج)'
print(clean_text(text))

dataset = read_dataset()

for t in dataset[:5]:
    print(t)
    print(clean_text(t))
    print('---------------------')
    break

non_letters = ' '.join(list(All_NON_Letters))
print(non_letters)
cleaned = clean_text(non_letters)
print(cleaned) # only tashkeel  and spaces left -> for now 
# print(PUNCTUATIONS)


# In[15]:


# Create X and Y to the model
# X is the input and Y is the output (the target)
# X is a list of all the characters in the dataset
# Y is a list of all Diacritics in the dataset (the target)
# if the character has no diacritic, the diacritic is set to be $ (empty diacritic)
from constants.arabic import HARAKAT,SHADDA,ARABIC_LETTERS
from train_collections import harakat2id
from tqdm import tqdm
import pandas as pd
train = read_dataset()


def xy_dataset(dataset,val_mode=False):
    """
    dataset: pandas series of the dataset (each example is a string)
    return: X, Y as lists
    """
    X = []
    X_words = []
    Y = []
    
    for line in tqdm(dataset):
        cleaned_line = clean_text(line)
        delimiters = [",", "|", ";","؛",".",":", "(" , ")","<",">","[","]","{","}"]
        splited_lines = re.split('['+''.join(map(re.escape, delimiters))+']', cleaned_line)
        for cleaned_line in splited_lines:
            
            if len(cleaned_line) < 1 or  (len(cleaned_line) < 4 and not val_mode):
                continue
            
            line_x = []
            line_y = []
            i = 0
            while i < len(cleaned_line):
                c = cleaned_line[i]
                line_x.append(c)
                
                # if this is the last character in the line or the next character is not a tashkeel 
                # then the tashkeel is empty
                if i == len(cleaned_line) - 1 or cleaned_line[i+1] not in HARAKAT:
                    line_y.append('$')
                    i += 1
                    continue
                
                i += 1
                tashkeel = cleaned_line[i]
                # if this is a shadda, we need to add the next character to the tashkeel
                # as shadda  ّ dont come alone
                if tashkeel == SHADDA and (i<len(cleaned_line) -1 and cleaned_line[i+1] in HARAKAT):
                    i += 1
                    tashkeel += cleaned_line[i]
                
                line_y.append(tashkeel)
                
                i+=1
            # add words to X_words
            X_words.append(''.join(line_x).split())
            X.append(line_x)
            Y.append(line_y)

    return X_words, X, Y
train_set = read_dataset()
X_words , X, Y = xy_dataset(train_set)



# make sure they are the same length (each x has a y of the same length)
for x, y in zip(X, Y):
    assert len(x) == len(y)


def convert_to_gold_standard_format(X, Y,name='train'):
    """
    X is a list of lists of characters
    Y is a list of lists of diacritics
    return is a csv file in the gold standard format 
    ID,label
    """
    pfile = pd.DataFrame(columns=['ID','letter','label'])
    pairs = []
    for sent, tags in zip(X, Y):
        for c, t in zip(sent, tags):
            if c in ARABIC_LETTERS:
                if t == '$':
                    t = ''
                pairs.append([c,harakat2id[t]])
                
    pfile['ID'] = [i for i in range(len(pairs))]  
    pfile['letter'] = [pair[0] for pair in pairs]
    pfile['label'] = [pair[1] for pair in pairs]
    pfile.to_csv(f"./clean_out/{name}_gold"+'.csv',index=False)
        
    
                
            
# save outs into 3 files in CLEAN_OUT_FOLDER   

def save_dataset(X, Y, X_words,x_file='X.csv', y_file='Y.csv', x_words_file='X_words.txt'):
    """
    save X, Y, X_words into 3 files in CLEAN_OUT_FOLDER
    """
    # make sure the folder exists
    if not os.path.exists(CLEAN_OUT_FOLDER):
        os.makedirs(CLEAN_OUT_FOLDER)
    # save X
    with open(os.path.join(CLEAN_OUT_FOLDER, x_file), 'w') as f:
        for line in X:
            f.write('s'.join(line) + '\n')
    
    # save Y
    with open(os.path.join(CLEAN_OUT_FOLDER, y_file), 'w') as f:
        for line in Y:
            f.write('s'.join(line) + '\n')
    
    # save X_words
    with open(os.path.join(CLEAN_OUT_FOLDER, x_words_file), 'w') as f:
        for line in X_words:
            f.write(' '.join(line) + '\n')

            
    
save_dataset(X, Y, X_words)

convert_to_gold_standard_format(X, Y)
    



# In[16]:


# val dataset too 
# val_dataset_f = os.path.join(DATASET_FOLDER, 'val.txt')
# read dataset as a text file and each line as a training example
val_dataset = read_dataset('val.txt', verbose=True)
X_words , X, Y = xy_dataset(val_dataset)
convert_to_gold_standard_format(X, Y,name='val')
save_dataset(X, Y, X_words, x_file='X_val.csv', y_file='Y_val.csv', x_words_file='X_words_val.txt')


# In[17]:


# val dataset too 
# val_dataset_f = os.path.join(DATASET_FOLDER, 'val.txt')
# read dataset as a text file and each line as a training example
val_dataset = read_dataset('demo.txt', verbose=True)
X_words , X, Y = xy_dataset(val_dataset, val_mode=True)
convert_to_gold_standard_format(X, Y,name='val')
save_dataset(X, Y, X_words, x_file='X_demo.csv', y_file='Y_demo.csv', x_words_file='X_words_demo.txt')


# In[ ]:


test_dataset = read_dataset('./test_no_diacritics.txt', verbose=True)
X_words , X, Y = xy_dataset(test_dataset,is_test=True)
convert_to_gold_standard_format(X, Y,name='test_no_diacritics')
save_dataset(X, Y, X_words, x_file='X_test_no_diacritics.csv', y_file='Y_test_no_diacritics.csv', x_words_file='test_no_diacritics.txt')


# In[18]:


def merge_all_text(file_names: list[str]):
    """
    takes a list of file names and merge them into one text file
    """
    with open(f'{CLEAN_OUT_FOLDER}/merged.txt', 'w') as outfile:
        for fname in file_names:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)
                    
cln_train = os.path.join(CLEAN_OUT_FOLDER, 'X_words.txt')
cln_val = os.path.join(CLEAN_OUT_FOLDER, 'X_words_val.txt')    
merge_all_text([cln_train, cln_val])


# In[19]:


train = read_dataset()
val = read_dataset('val.txt')
with open(f'{CLEAN_OUT_FOLDER}/merged_unsplited.txt', 'w',encoding="utf8") as infile:
    trainfile = open(f'{CLEAN_OUT_FOLDER}/train_unsplited.txt','w', encoding="utf8")
    valfile = open(f'{CLEAN_OUT_FOLDER}/val_unsplited.txt','w', encoding="utf8")
    # keep only arabic letters and spaces
    for t in train:
        ll = ''.join([c for c in t if c in ARABIC_LETTERS or c == ' '])
        ll = re.sub(r'\s+', ' ', ll)+ '\n'
        trainfile.write(ll)
        infile.write(ll)
        
    for t in val:
        ll = ''.join([c for c in t if c in ARABIC_LETTERS or c == ' ']) 
        ll = re.sub(r'\s+', ' ', ll)+ '\n'
        valfile.write(ll)
        infile.write(ll)
        



# In[ ]:





# In[ ]:





# In[20]:


from nltk.stem.arlstem import ARLSTem

stemmer = ARLSTem()
stemmer.stem('المدرسة')




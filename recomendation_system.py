import re
import threading
import queue
import word2vec
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import re
import nltk
import pymorphy2
nltk.download('stopwords')
from nltk.corpus import stopwords

df = pd.read_csv('preprocessed_data.csv')
df['text']= df['text'].astype(str)
df['text'] = df['text'].apply(lambda x: x.split())
voc = []
for i in df['text']:
    voc.append(i)
model = Word2Vec(voc, size=10, window=5, min_count=1, workers=4)
df['vector'] = df['text'].apply(lambda x: model[x].mean(axis=0))
for i in range(10):
    df[f"f{i}"] = df.vector.apply(lambda x: x[i])
    
neigh = KNeighborsClassifier(n_neighbors=3)
x_train, x_test, y_train, y_test = train_test_split(df.loc[:, 'f0':'f9'], df['category_id'].values, test_size=0.3, random_state=142)
neigh.fit(x_train, y_train)

def predict(x_test):
    feat = []
    for i in x_test:
        feat.append(i)
    feat = np.array(feat).reshape(-1, 10)
    return neigh.predict(feat)

def nearest(req, df, n):
    distances = pd.DataFrame(columns=['dist'])
    print(req)
    print(df.shape)
    distances['dist'] = df['vector'].apply(lambda x: np.linalg.norm(req-x))
    df['dist'] = distances['dist']
    mins = df.nsmallest(n=n, columns='dist')
    arr = mins[['title', 'descrirption', 'product_id']].values.tolist()
    brr = []
    for i in arr:
        brr.append(i[0]+ ", " + i[1] + " №" + i[2])
    return brr

def preprocess_text(text):
    stop_rus = stopwords.words("russian")
    stop_rus_set = set(stop_rus)
    morph = pymorphy2.MorphAnalyzer()
    letters_only = re.sub(r"\W", " ", str(text), flags=re.U)
    letters_only = re.sub(r'[^\w\s]+|[\d]+', '', letters_only, flags=re.U)
    words = letters_only.lower().split()
    meaningful_words = [morph.parse(w)[0].normal_form for w in words if not w in stop_rus_set]
    return " ".join(meaningful_words).split()

def vectorizing(req):    
    return model[preprocess_text(req)].mean(axis=0)


def result(s):
    try:
        r=vectorizing(s)
    except KeyError:
        return ["НЕ найдено"]
    ans = nearest(r, df, 5)
    ans.insert(0, "Категория: " + str(predict(r)[0]))
    return ans
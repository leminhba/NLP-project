import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.DataFrame(columns=["ID","DESCRIPTION"], data=np.matrix([[10,"Cancel ASN WMS Cancel ASN"],
                                                                [11,"MAXPREDO Validation is corect"],
                                                                [12,"Move to QC"],
                                                                [13,"Cancel ASN WMS ASN"],
                                                                [14,"MAXPREDO Validation is right"],
                                                                [15,"Verify files are sent every hours for this interface from Optima"],
                                                                [16,"MAXPREDO Validation are correct"],
                                                                [17,"Move to QC"],
                                                                [18,"Verify files are not sent"]
                                                                ]))

corpus = list(df["DESCRIPTION"].values)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)

threshold = 0.4

for x in range(0,X.shape[0]):
  for y in range(x,X.shape[0]):
    if(x!=y):
      if(cosine_similarity(X[x],X[y])>threshold):
        print(df["ID"][x],":",corpus[x])
        print(df["ID"][y],":",corpus[y])
        print("Cosine similarity:",cosine_similarity(X[x],X[y]))
        print()
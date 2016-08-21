import pandas as pd
import datetime
from gensim import corpora, models, similarities
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
MDATA_DIR = "../mdata/"
MODEL_DIR = "../models/lsi/"
"""
Based the inter_score, build the dictionary
"""
def build_dictionary():
	fr = open(MDATA_DIR + "inter_score.csv")
	header = fr.readline()
	sens = []
	for line in fr:
		words = []
		for term in line[:-1].split("\t")[1].split(","):
			iid = term.split(":")[0]
			words.append(iid)
		sens.append(words)
	dictionary = corpora.Dictionary(sens)
	dictionary.save(MODEL_DIR + 'item.dict.lsi')
"""
Based the inter_score, build the LSI model
"""
def build_model():
	fr = open(MDATA_DIR + "inter_score.csv")
	header = fr.readline()
	sens = []
	for line in fr:
		words = []
		for term in line[:-1].split("\t")[1].split(","):
			iid = term.split(":")[0]
			rat = int(term.split(":")[1])
			words += [iid for i in range(rat)]
		sens.append(words)
	dic = corpora.Dictionary.load(MODEL_DIR + "item.dict.lsi")
	corpus = [dic.doc2bow(text) for text in sens]
	tfidf = models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]

	lsi = models.LsiModel(corpus_tfidf, id2word=dic, num_topics=50)
	lsi.save(MODEL_DIR + "cf.lsi.model")
"""
Compute the similarity based LSI model
"""
def user_similarity():
	lsi = models.LsiModel.load(MODEL_DIR + "cf.lsi.model")
	ratings = pd.read_csv(MDATA_DIR + "inter_score.csv", sep="\t", index_col=0)

	items = pd.read_csv("../data/items.csv", sep="\t", index_col=0)
	active_items = items[items['active_during_test'] == 1]

	target_users = pd.read_csv("../data/target_users.csv", sep="\t")
	target_users = target_users['user_id'].unique()

	corpus = []
	lineuid = []
	fw = open(MDATA_DIR + "user_similar_cf.csv", "w")
	fw.write("user_id\tneighs\n")
	for index, row in ratings.iterrows():
		words = []
		for term in row['score'].split(",")[:30]:
			iid = term.split(":")[0]
			rat = int(term.split(":")[1])
			words += [iid for i in range(rat)]
		corpus.append(words)
		lineuid.append(index)

	dic = corpora.Dictionary.load(MODEL_DIR + "item.dict.lsi")
	corpus = [dic.doc2bow(text) for text in corpus]
	tfidf = models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]
	corpus_index = similarities.MatrixSimilarity(lsi[corpus_tfidf])
	
	count = 1
	print ratings.shape[0]
	for uid in target_users:
		if uid not in ratings.index:
			continue
		words = []
		row = ratings.ix[uid,'score']
		for term in row.split(",")[:30]:
			iid = term.split(":")[0]
			rat = int(term.split(":")[1])
			words += [iid for i in range(rat)]
		query_bow = dic.doc2bow(words)
		query_lsi = lsi[tfidf[query_bow]]

		sims = corpus_index[query_lsi]
		sort_sims = sorted(enumerate(sims), key=lambda x: -x[1])[:20]
		nei_list = []
		for key,value in sort_sims:
			if lineuid[key] == uid:
				continue
			if value < 0.5:
				break
			nei_list.append(str(lineuid[key])+":"+str(round(value,6)))
		if len(nei_list) > 0:
			fw.write(str(uid)+"\t"+",".join(nei_list)+"\n")
		count+=1
		if count % 100 == 0:
			print count
	fw.close()
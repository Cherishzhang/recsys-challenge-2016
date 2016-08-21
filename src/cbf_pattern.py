import pandas as pd
import datetime
from gensim.models.word2vec import LineSentence, Word2Vec
from gensim.models.doc2vec import Doc2Vec, LabeledSentence
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
MDATA_DIR = "../mdata/"
MODEL_DIR = "../models/word2vec/"
"""
Contruct the corpus for word2vec
"""
def construct_sentences():
	items = pd.read_csv("../data/items.csv", sep="\t")
	fw = open(MODEL_DIR+"sentences.csv", "w")
	for index, row in items.iterrows():
		title = str(row['title'])
		tags = str(row['tags'])
		if title == "nan" or tags == "nan":
			continue
		words = title.split(",") + title.split(",")+tags.split(",")
		fw.write(" ".join(words) + "\n")
	fw.close()

"""
Construct the corpus for doc2vec
"""
class LabeledLineSentence(object):
	def __init__(self, fn):
		self.filename = fn
	def __iter__(self):
		items = pd.read_csv(self.filename, sep="\t")
		for index, row in items.iterrows():
			title = str(row['title'])
			tags = str(row['tags'])
			if title == "nan" or tags == "nan":
				continue
			ws = title.split(",") + title.split(",")+tags.split(",")
			yield LabeledSentence(ws,['SENT_%s' % str(row['id'])])
"""
Build the word2vec
"""
def build_word2vec():
	sentences = LineSentence(MODEL_DIR + 'sentences.csv')
	model = Word2Vec(sentences, size=100, window=10, min_count=5, workers=4)
	model.save(MODEL_DIR + "w2v.model")
"""
Build the doc2vec
"""
def build_doc2vec():
	sentences = LabeledLineSentence("../data/items.csv")
	model = Doc2Vec(sentences, size=100, window=8, min_count=5, workers=4)
	model.save(MODEL_DIR + "d2v.model")
"""
Compute the similarity score of inter_score pair in content(doc2vec)
"""			
def get_similar_items(beg=0, items_len=10000, fpath=MDATA_DIR+"item_similar_cbf.csv"):
	model = Doc2Vec.load(MODEL_DIR + "d2v.model")
	ratings = pd.read_csv(MDATA_DIR + "inter_score.csv", sep="\t", index_col=0)

	items = pd.read_csv("../data/items.csv", sep="\t", index_col=0)
	active_items = items[items['active_during_test'] == 1]

	iid_list = set()
	for index, row in ratings.iterrows():
		for term in row['score'].split(",")[:30]:
			iid = int(term.split(":")[0])
			iid_list.add(iid)
	fw = open(fpath, "w")
	fw.write("item_id\tneighs\n")
	count = 0
	error_count = 0
	for iid in iid_list:
		sen = "SENT_"+str(iid)
		count += 1
		if count < beg:
			continue
		if count % 100 == 0:
			print len(iid_list), count, error_count
		neigh_list = []
		try:
			sims = model.docvecs.most_similar(sen, topn=20)
			for term in sims:
				sid = int(term[0][5:])
				score = term[1]
				if sid not in active_items.index:
					continue
				neigh_list.append(str(sid)+":"+str(round(score,6)))
		except KeyError:
			error_count += 1

		if len(neigh_list) > 0:
			fw.write(str(iid)+"\t"+",".join(neigh_list)+"\n")
		if count - beg == items_len:
			break
	fw.close()
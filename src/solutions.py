import pandas as pd
import numpy as np
import sys
target_users = pd.read_csv("../data/target_users.csv",sep="\t")
target_users = target_users['user_id'].unique()

MDATA_DIR = "../mdata/"
"""
Convert dataframe to dict
"""
def df2dict(df, col='score',topn=30):
	df_dict = dict()
	for index, row in df.iterrows():
		df_dict[index] = []
		for term in row[col].split(",")[:topn]:
			tid = int(term.split(":")[0])
			w = float(term.split(":")[1])
			df_dict[index].append([tid, w])
	return df_dict
"""
This generates a solution: rec by history inter

"""
def solution1():
	global target_users, MDATA_DIR
	inter_rec = pd.read_csv(MDATA_DIR + "inter_rec.csv", sep="\t", index_col=0)
	user_rec = dict()
	count = 0
	for uid in target_users:
		if uid in inter_rec.index:
			user_rec[uid] = map(int, inter_rec.ix[uid,'items'].split(","))[:30]
		count+=1
		if count % 5000 == 0:
			print count

	result = pd.DataFrame({'user_id':user_rec.keys(), 'recommended_items': [",".join(map(str, i[:30])) for i in user_rec.values()]})
	result = result.sort(columns=['user_id'], axis=0)
	result[['user_id','recommended_items']].to_csv("../output/approach1.csv", sep="\t",index=False)
"""
This generates a solution: rec by history imp 
"""
def solution2():
	global target_users, MDATA_DIR
	imp_rec = pd.read_csv(MDATA_DIR + "imp_rec.csv", sep="\t", index_col=0)
	user_rec = dict()
	count = 0
	for uid in target_users:
		if uid in imp_rec.index:
			user_rec[uid] = map(int, inter_rec.ix[uid,'items'].split(","))[:30]
		count+=1
		if count % 5000 == 0:
			print count

	result = pd.DataFrame({'user_id':user_rec.keys(), 'recommended_items': [",".join(map(str, i[:30])) for i in user_rec.values()]})
	result = result.sort(columns=['user_id'], axis=0)
	result[['user_id','recommended_items']].to_csv("../output/approach2.csv", sep="\t",index=False)

"""
This generates a solution: rec by solution1,2 + cf
"""
def solution3():
	global target_users, MDATA_DIR
	inter_rec = pd.read_csv(MDATA_DIR + "inter_rec.csv", sep="\t", index_col=0)
	imp_rec = pd.read_csv(MDATA_DIR + "imp_rec.csv", sep="\t", index_col=0)
	pop_rec = pd.read_csv(MDATA_DIR + "pop_rec.csv", sep="\t")
	inter_score = pd.read_csv(MDATA_DIR + "inter_score.csv", sep="\t", index_col=0)
	user_sim = pd.read_csv(MDATA_DIR + "user_similar_cf.csv", sep="\t", index_col=0)

	inter_score = df2dict(inter_score, 'items', 100)
	user_sim = df2dict(user_sim, 'neighs', 100)

	user_rec = dict()
	count = 0
	for uid in  target_users:
		user_rec[uid] = []
		if uid in inter_rec.index:
			user_rec[uid] = map(int, inter_rec.ix[uid,'items'].split(",")[:25])
		if uid  in imp_rec.index:
			for iid in map(int, imp_rec.ix[uid,'items'].split(",")):
				if iid in user_rec[uid]:
					continue
				user_rec[uid].append(iid)
		if len(user_rec[uid]) >= 30:
			continue
		if uid in user_sim:
			candi_dict = dict()
			for nid, w in user_sim[uid]:
				if nid not in inter_score:
					continue
				for iid, rat in inter_score[nid]:
					if iid not in candi_dict:
						candi_dict[iid] = rat*w
					else:
						candi_dict[iid] += rat*w

			for iid, score in sorted(candi_dict.iteritems(), key=lambda x: -x[1])[:10]:
				if iid not in user_rec[uid]:
					user_rec[uid].append(iid)

		if len(user_rec[uid]) < 30:
			for iid in pop_rec['item_id']:
				if iid in user_rec[uid]:
					continue
				user_rec[uid].append(iid)
				if len(user_rec[uid]) >= 30:
					break
		count += 1
		if count % 1000 == 0:
			print count

	result = pd.DataFrame({'user_id':user_rec.keys(), 'recommended_items': [",".join(map(str, i[:30])) for i in user_rec.values()]})
	result = result.sort(columns=['user_id'], axis=0)
	result[['user_id','recommended_items']].to_csv("../output/approach3.csv", sep="\t",index=False)

"""
This generates a solution: rec by solution1,2 + cbf
"""
def solution4():
	global target_users, MDATA_DIR
	inter_rec = pd.read_csv(MDATA_DIR + "inter_rec.csv", sep="\t", index_col=0)
	imp_rec = pd.read_csv(MDATA_DIR + "imp_rec.csv", sep="\t", index_col=0)
	pop_rec = pd.read_csv(MDATA_DIR + "pop_rec.csv", sep="\t")

	inter_score = pd.read_csv(MDATA_DIR + "inter_score.csv", sep="\t", index_col=0)
	item_sim = pd.read_csv(MDATA_DIR + "item_similar_cbf.csv", sep="\t", index_col=0)
	inter_score = df2dict(inter_score, 'items', 100)
	item_sim = df2dict(item_sim, 'neighs', 100)

	user_rec = dict()
	count = 0
	for uid in target_users:
		user_rec[uid] = []
		if uid in inter_rec.index:
			user_rec[uid] = map(int, inter_rec.ix[uid,'items'].split(",")[:25])
		if uid  in imp_rec.index:
			for iid in map(int, imp_rec.ix[uid,'items'].split(",")):
				if iid in user_rec[uid]:
					continue
				user_rec[uid].append(iid)
		if len(user_rec[uid]) >= 30:
			continue
		if uid in inter_score:
			candi_dict = dict()
			for iid, rat in inter_score[uid]:
				if iid not in item_sim:
					continue
				for sid, w in item_sim[iid]:
					if sid in candi_dict:
						candi_dict[sid] += w*rat
					else:
						candi_dict[sid] = w*rat
			
			for iid, score in sorted(candi_dict.iteritems(), key=lambda x: -x[1])[:10]:
				if iid not in user_rec[uid]:
					user_rec[uid].append(iid)

		if len(user_rec[uid]) < 30:
			for iid in pop_rec['item_id']:
				if iid in user_rec[uid]:
					continue
				user_rec[uid].append(iid)
				if len(user_rec[uid]) >= 30:
					break
		count += 1
		if count % 1000 == 0:
			print count

	result = pd.DataFrame({'user_id':user_rec.keys(), 'recommended_items': [",".join(map(str, i[:30])) for i in user_rec.values()]})
	result = result.sort(columns=['user_id'], axis=0)
	result[['user_id','recommended_items']].to_csv("../output/approach4.csv", sep="\t",index=False)
"""
This generates a solution: rec by ensemble above
"""
def solution5():
	global target_users, MDATA_DIR
	inter_rec = pd.read_csv(MDATA_DIR + "inter_rec.csv", sep="\t", index_col=0)
	imp_rec = pd.read_csv(MDATA_DIR + "imp_rec.csv", sep="\t", index_col=0)
	pop_rec = pd.read_csv(MDATA_DIR + "pop_rec.csv", sep="\t")

	inter_score = pd.read_csv(MDATA_DIR + "inter_score.csv", sep="\t", index_col=0)
	user_sim = pd.read_csv(MDATA_DIR + "user_similar_cf.csv", sep="\t", index_col=0)
	item_sim = pd.read_csv(MDATA_DIR + "item_similar_cbf.csv", sep="\t",index_col=0)

	inter_score = df2dict(inter_score, 'items', 100)
	user_sim = df2dict(user_sim, 'neighs', 100)
	item_sim = df2dict(item_sim, 'neighs', 100)
	user_rec = dict()
	count = 0
	for uid in target_users:
		user_rec[uid] = []
		if uid in inter_rec.index:
			user_rec[uid] = map(int, inter_rec.ix[uid,'items'].split(",")[:25])
		if uid  in imp_rec.index:
			for iid in map(int, imp_rec.ix[uid,'items'].split(",")):
				if iid in user_rec[uid]:
					continue
				user_rec[uid].append(iid)
		if len(user_rec[uid]) >= 30:
			continue
		candi_dict = dict()
		max_cf = 0
		max_cbf = 0
		if uid in inter_score: ##cbf
			for nid, rat in inter_score[uid]:
				if nid not in item_sim:
					continue
				for iid, w in item_sim[nid]:
					if iid not in candi_dict:
						candi_dict[iid] = [0,0]
						candi_dict[iid][0] = rat*w
					else:
						candi_dict[iid][0] += rat*w
					if candi_dict[iid][0] > max_cbf:
						max_cbf = candi_dict[iid][0]

		if uid in user_sim:  ##cf
			for nid, w in user_sim[uid]:
				if nid not in inter_score:
					continue
				for iid, rat in inter_score[nid]:
					if iid not in candi_dict:
						continue
					candi_dict[iid][1] += rat*w
					if candi_dict[iid][1] > max_cf:
						max_cf = candi_dict[iid][1]

		for iid, score in sorted(candi_dict.iteritems(), key=lambda x: 0.95*x[1][0]/(max_cbf+0.1)+0.05*x[1][1]/(max_cf+0.1))[:10]:
			if iid not in user_rec[uid]:
				user_rec[uid].append(iid)

		if len(user_rec[uid]) < 30:
			for iid in pop_rec['item_id']:
				if iid in user_rec[uid]:
					continue
				user_rec[uid].append(iid)
				if len(user_rec[uid]) >= 30:
					break
		count += 1
		if count % 1000 == 0:
			print count
	result = pd.DataFrame({'user_id':user_rec.keys(), 'recommended_items': [",".join(map(str, i[:30])) for i in user_rec.values()]})
	result = result.sort(columns=['user_id'], axis=0)
	result[['user_id','recommended_items']].to_csv("../output/approach5.csv", sep="\t",index=False)



if __name__ == "__main__":
	if len(sys.argv) == 1:
		print "please input the approach num\n"
	else:
		choice = sys.argv[1]
		if choice == '1':
			solution1()
		elif choice == '2':
			solution2()
		elif choice == '3':
			solution3()
		elif choice == '4':
			solution4()
		elif choice == "5":
			solution5()







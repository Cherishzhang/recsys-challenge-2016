import pandas as pd
import numpy as np
import datetime
import sys
"""
Transform implicit feedback to score, click:1, bookmark/apply:5
"""
MDATA_DIR = "../mdata/"
def implicit_to_score():
	print "begin convert implicit feedback to score"
	target_users = pd.read_csv("../data/target_users.csv",sep="\t")
	target_users = target_users['user_id'].unique()

	inter = pd.read_csv("../data/interactions.csv", sep="\t")
	inter = inter[(inter['interaction_type'] < 4) & (inter['user_id'].isin(target_users))] #only consider positive interactions
	inter = inter.sort(columns=['interaction_type','created_at'], axis=0, ascending=False)

	user_inter = dict()
	count_row = 0
	for uid, group in inter.groupby(['user_id']):
		click = list(group[group['interaction_type'] == 1]['item_id'])
		like = list(group[group['interaction_type'] > 1]['item_id'])

		items_score = dict()
		for iid in np.unique(like):#score the bookmark and apply actions
			items_score[iid] = 5
		for iid in np.unique(click):
			if iid in items_score:
				continue
			count = click.count(iid)
			if count > 2:
				items_score[iid] = 3
			else:
				items_score[iid] = 1
		line = []
		for iid in group['item_id'].unique():
			if iid in items_score:
				line.append(str(iid)+":"+str(int(items_score[iid])))
		if line != []:
			user_inter[uid] = line
		count_row += 1
		if count_row % 5000 == 0:
			print count_row

	result = pd.DataFrame({'user_id':user_inter.keys(), 'items': [",".join(i) for i in user_inter.values()]})
	result = result.sort(columns=['user_id'], axis=0)
	result[['user_id','items']].to_csv(MDATA_DIR+"inter_score.csv", sep="\t",index=False)
	print "saved the score to inter_score.csv"

"""
Filter the inter by active items, which can make recommendations to users by history
"""
def generate_inter_cands():
	target_users = pd.read_csv("../data/target_users.csv", sep="\t")
	target_users = target_users['user_id'].unique()

	items = pd.read_csv("../data/items.csv", sep="\t")
	active_items = set(items[items['active_during_test'] == 1]['id'].unique())

	inter_score = pd.read_csv(MDATA_DIR+"inter_score.csv", sep="\t", index_col=0)
	inter_score = inter_score[inter_score.index.isin(target_users)]
	user_rec = dict()
	for uid, row in inter_score.iterrows():
		user_rec[uid] = []
		for term in row['items'].split(","):
			iid = int(term.split(":")[0])
			if iid in active_items:
				user_rec[uid].append(str(iid))
		if user_rec[uid] == []:
			del user_rec[uid]

	result = pd.DataFrame({'user_id':user_rec.keys(), 'items': [",".join(i) for i in user_rec.values()]})
	result = result.sort(columns=['user_id'], axis=0)
	result[['user_id','items']].to_csv(MDATA_DIR+"inter_rec.csv", sep="\t",index=False) 

"""
Filter the past four weeks impression by active items, which can make recommendations to users by original system.
"""
def generate_imp_cands():
	target_users = pd.read_csv("../data/target_users.csv", sep="\t")
	target_users = target_users['user_id'].unique()

	items = pd.read_csv("../data/items.csv", sep="\t")
	active_items = set(items[items['active_during_test'] == 1]['id'].unique())

	imp45 = pd.read_csv("../data/week45.csv", sep="\t", index_col=0, header=None, names=['user_id', 'items']) #load the impression data
	imp44 = pd.read_csv("../data/week44.csv", sep="\t", index_col=0, header=None, names=['user_id', 'items'])
	imp43 = pd.read_csv("../data/week43.csv", sep="\t", index_col=0, header=None, names=['user_id', 'items'])
	imp42 = pd.read_csv("../data/week42.csv", sep="\t", index_col=0, header=None, names=['user_id', 'items'])

	user_rec = dict()
	for uid in target_users:
		iid_list = []
		if uid in imp45.index:
			for iid in map(int, imp45.ix[uid,'items'].split(",")):
				if iid in active_items:
					iid_list.append(iid)
		elif uid in imp44.index:
			for iid in map(int, imp44.ix[uid,'items'].split(",")):
				if iid in active_items:
					iid_list.append(iid)
		elif uid in imp43.index:
			for iid in map(int, imp43.ix[uid,'items'].split(",")):
				if iid in active_items:
					iid_list.append(iid)
		elif uid in imp42.index:
			for iid in map(int, imp42.ix[uid,'items'].split(",")):
				if iid in active_items:
					iid_list.append(iid)
		if iid_list != []:
			user_rec[uid] = iid_list

	result = pd.DataFrame({'user_id':user_rec.keys(), 'items': [",".join(map(str, i)) for i in user_rec.values()]})
	result = result.sort(columns=['user_id'], axis=0)
	result[['user_id','items']].to_csv(MDATA_DIR+"imp_rec.csv", sep="\t",index=False) 

"""
Generate the popular item list
"""
def generate_pop_cands():
	items = pd.read_csv("../data/items.csv", sep="\t")
	active_items = set(items[items['active_during_test'] == 1]['id'].unique())

	imp45 = pd.read_csv("../imp/week45.csv", sep="\t", index_col=0, header=None, names=['user_id','items'])
	pop_dict = dict()
	for index, row in imp45.iterrows():
		iid_list = set(map(int, str(row['items']).split(",")))
		for iid in iid_list:
			if iid not in pop_dict:
				pop_dict[iid] = 0
			pop_dict[iid] += 1

	result = pd.DataFrame({'item_id':pop_dict.keys(), 'pop': pop_dict.values()})
	result = result.sort(columns=['pop'], axis=0, ascending=False)
	result[['item_id','pop']].to_csv(MDATA_DIR+"pop_rec.csv", sep="\t",index=False)


if __name__ == "__main__":
	if len(sys.argv) == 1:
		print "cmd : 1. implicit_to_score\n 2.generate_inter_list\n 3.generate_imp_list\n 4.generate_pop_list\n"
	else:
		choice = sys.argv[1]
		if choice == '1':
			implicit_to_score()
		elif choice == '2':
			generate_inter_cands()
		elif choice == '3':
			generate_imp_cands()
		elif choice == '4':
			generate_pop_cands()
    

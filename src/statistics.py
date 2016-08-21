import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import datetime
import powerlaw
from pylab import setp
from mpl_toolkits.axes_grid.inset_locator import inset_axes
MDATA_DIR = "../mdata/"
"""
Plot figure 1 in the paper
"""
def power_law():
	inter = pd.read_csv("../data/interactions.csv", sep="\t")
	inter = inter[inter['interaction_type'] == 2]
	target_users = pd.read_csv("../data/target_users.csv")
	items = pd.read_csv("../data/items.csv", sep="\t")
	active_items = items[items['active_during_test'] == 1]

	c1 = inter['user_id'].value_counts()
	c2 = inter['item_id'].value_counts()
	target_users['pop'] = target_users['user_id'].apply(lambda x: c1[x]+1 if x in c1 else 1)
	active_items['pop'] = active_items['id'].apply(lambda x: c2[x]+1 if x in c2 else 1)
	#target_users['counts'] = target_users.groupby(['pop'])['user_id'].transform('count')
	fig = plt.figure(figsize=(3,2))
	ax1 = fig.add_subplot(1,2,1)
	ax2 = fig.add_subplot(1,2,2)
	fig.subplots_adjust(left=-0.2, bottom=None, right=None, top=None, wspace=.3, hspace=.2)
	#plot user figure
	#powerlaw.Distribution(discrete_approximation="round")
	powerlaw.plot_pdf(target_users['pop'].values, ax=ax1, color='b')
	powerlaw.plot_pdf(target_users['pop'].values, linear_bins=True, ax=ax1, color='r')
	ax1in = inset_axes(ax1, width = "30%", height = "30%", loc=3)
	ax1in.hist(target_users['pop'].values, normed=True, color='b')
	ax1in.set_xticks([])
	ax1in.set_yticks([])
    #plot item figure
	ax2.set_ylim(ax1.get_ylim())
	setp( ax2.get_yticklabels(), visible=False)
	#setp( ax1.get_yticklabels(), visible=False)
	powerlaw.plot_pdf(active_items['pop'].values, ax=ax2, color='b')
	powerlaw.plot_pdf(active_items['pop'].values, ax=ax2, linear_bins=True, color='r')
	ax2in = inset_axes(ax2, width = "30%", height = "30%", loc=3)
	ax2in.hist(active_items['pop'].values, normed=True, color='b')
	ax2in.set_xticks([])
	ax2in.set_yticks([])
	ax1.set_xlabel('target users',fontsize=10)
	ax2.set_xlabel("active items", fontsize=10)
	fig.savefig(MDATA_DIR + 'ui.eps', bbox_inches='tight')
power_law()

"""
Plot figure 2 in the paper
"""
def user_item_relation():
	inter = pd.read_csv("../data/interactions.csv", sep="\t")
	inter['week'] = inter['created_at'].apply(lambda x: datetime.datetime.utcfromtimestamp(x).isocalendar()[1])
	inter = inter[(inter['interaction_type'] < 4) & (inter['week'] == 44)]
	inter = inter.drop_duplicates(['user_id','item_id','interaction_type'], keep="first")

	##each item is interacted by how many users
	inter['icounts'] = inter.groupby(['item_id'])['user_id'].transform('count')

	#inter = inter[(inter['interaction_type'] >= 1) & (inter['interaction_type'] <= 3) ]
	##each user interacts with item, denote the users' liveness
	inter['ucounts'] = inter.groupby(['user_id'])['item_id'].transform('count')
	df = inter.sample(frac=0.01)
	#df[['ucounts', 'icounts']].to_csv("relation.csv", sep=",", index=False)

	f1 = plt.figure(figsize=(8,6))
	ax1 = f1.add_subplot(1,1,1)
	ax1.scatter(df['ucounts'].values,df['icounts'].values,s=np.pi*(5**2),alpha=0.01,c='r')
	ax1.set_xticks([0,100,200,300])
	ax1.set_yticks([0,500,1000,1500])
	ax1.set_xticklabels(('0','1','2','3'), fontsize=20)
	ax1.set_yticklabels(('0', '5', '10', '15'), fontsize=20)
	ax1.set_xlabel('user activity', fontsize=20)
	ax1.set_ylabel("item popularity", fontsize=20)
	f1.savefig(MDATA_DIR + "relation.eps",dpi=72)

def stat_of_targets():
	target_users = pd.read_csv("../data/target_users.csv", sep="\t")
	items = pd.read_csv("../data/items.csv", sep="\t")
	inter = pd.read_csv("../data/interactions.csv", sep="\t")
	history_users = target_users[target_users['user_id'].isin(inter['user_id'].unique())]
	print "total target users: ", target_users.shape[0]
	print "---history users: ", history_users.shape[0]
	print "---cold start users: ", target_users.shape[0] - history_users.shape[0]
	active_items = items[items['active_during_test'] == 1]
	history_items = active_items[active_items['id'].isin(inter['item_id'].unique())]
	print "total active items: ", active_items.shape[0]
	print "---history items: ", history_items.shape[0]
	print "---cold start items: ", active_items.shape[0] - history_items.shape[0]

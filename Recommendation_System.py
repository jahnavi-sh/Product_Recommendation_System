#First, understanding objective of the project -
#Understand the overall buying behaviour of our customer. Build a ML recommending system
#that recommends products to the customers. 

#Collaborative filtering algorithm 

#import the required python libraries 
import numpy as np 
import pandas as pd 
from pandas import DataFrame
from scipy import sparse 
from pandas.api.types import CategoricalDtype 

#load the data into pandas' dataframe 
df = pd.read_excel('sales.xlsx')  

#view the first five rows of the dataset 
df.head()

#It consists of the following columns - 
#1. SalesDate 
#2. SalesValue
#3. SalesAmount 
#4. Customer 
#5. SalesTransactiomID
#6. SalesItem

#Features relevant to our recpmmendation system - Sales per day, customer, sales item 
#we can simply drop the rest 

df = df[[‘SalesItem’, ‘SalesAmount’, ‘Customer’]] 
df.head()

#getting more information about the dataset 
df.info()

#There are no null values 

df.groupby([‘Customer’,‘SalesItem’]).sum()

customers = list(np.sort(df.Customer.unique()))
products = list(df.SalesItem.unique()) 
quantity = list(df.SalesAmount)

#Using Panda’s DataFrame we can converge Numpy’s list back into a Panda’s dataframe:
DfCustomerUnique = DataFrame(customers,columns=[‘Customer’]) 
DfCustomerUnique.head()

#Now we can build our sparse matrix:

rows = df.Customer.astype(CategoricalDtype(categories=customers)).cat.codes 
# We have got 35 unique customers, which make up 13837 data rows (index) 
# Get the associated row indices 
cols = df.SalesItem.astype(CategoricalDtype(categories= products)).cat.codes 
# We have got unique 3725 SalesItems, making up 13837 data rows (index) 
# Get the associated column indices 
#Compressed Sparse Row matrix 
PurchaseSparse = sparse.csr_matrix((quantity, (rows, cols)), shape=(len(customers), len(products))) 

MatrixSize = PurchaseSparse.shape[0]*PurchaseSparse.shape[1]
PurchaseAmount = len(PurchaseSparse.nonzero()[0]) 
sparsity = 100*(1 - (PurchaseAmount/MatrixSize))
sparsity

def create_DataBinary(df):
DataBinary = df.copy()DataBinary['PurchasedYes'] = 1
return DataBinary
DataBinary = create_DataBinary(df)
DataBinary.head()

#let’s get rid of the column SalesAmount:
purchase_data=DataBinary.drop(['SalesAmount'], axis=1)
purchase_data.head()

#Item Customer Matrix 
purchase_data[‘SalesItem’] = ‘I’ + purchase_data[‘SalesItem’].astype(str) 
DfMatrix = pd.pivot_table(purchase_data, values=’PurchasedYes’, index=’Customer’, columns=’SalesItem’)
DfMatrix.head()

#turn pivot table into desired format 
#reset_index, rename_axis
DfResetted = DfMatrix.reset_index().rename_axis(None, axis=1) 
DfResetted.head() 

DfResetted = DfMatrix.reset_index().rename_axis(None, axis=1) 
DfResetted.head() 

#create dataframe that only includes sales items, customer is indexed instead 
DfSalesItem = df.drop(‘Customer’, 1) 
DfSalesItem.head()

#calculate item based recommendation
DfSalesItemNorm = DfSalesItem/np.sqrt(np.square(DfSalesItem).sum(axis=0))   
DfSalesItemNorm.head()

#.dot vectors to compute cosine similarities 
ItemItemSim = DfSalesItemNorm.transpose().dot(DfSalesItemNorm) 
ItemItemSim.head()

#Create a placeholder items for closest neighbours to an item
ItemNeighbours = pd.DataFrame(index=ItemItemSim.columns,columns=range(1,10))
ItemNeighbours.head()

#loop through similarity dataframe and fill in neighbouring item names 
for i in range(0,len(ItemItemSim.columns)): 
    ItemNeighbours.iloc[i,:9] = ItemItemSim.iloc[0:,i].sort_values(ascending=False)[:9].index 
    #recommend only 9 items at a time 

ItemNeighbours.head().iloc[:11,1:9]

#create a place holder matrix for similarities, and fill in the customer column
CustItemSimilarity = pd.DataFrame(index=df.index,columns=df.columns) 
CustItemSimilarity.iloc[:,:1] = df.iloc[:,:1] 
CustItemSimilarity.head()

#calculate the similarity scores
def getScore(history, similarities):
return sum(history*similarities)/sum(similarities)

#generate matrix of customer based recommendations
# Get the top SalesItems 
CustItemRecommend = pd.DataFrame(index=CustItemSimilarity.index, columns=[‘Customer’,’1',’2',’3',’4',’5',’6']) 
CustItemRecommend.head()

#see product names 
for i in range(0,len(CustItemSimilarity.index)): 
    CustItemRecommend.iloc[i,1:] = CustItemSimilarity.iloc[i,:].sort_values(ascending=False).iloc[1:7,].index.transpose() 
CustItemRecommend.head()
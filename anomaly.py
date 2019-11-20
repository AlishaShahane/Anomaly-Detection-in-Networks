#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: alishashahane
"""

from statistics import median
import sys
import networkx as nx
from os import listdir
import hashlib
import matplotlib.pyplot as plt

class Anomaly():

    def get_FileList(self, dataDirectory):
        # Description: For the given input dataset, returns a list of files in it.
        
    	if dataDirectory[len(dataDirectory) - 1] != "/":
    		dataDirectory = dataDirectory + "/"

    	fileList = sorted(listdir(dataDirectory), key = lambda f: (int(f.partition('_')[0])) )
    	return [dataDirectory + x for x in fileList]
    
    def get_SimHashList(self, files):
        # Description: For every file, create a graph anf its feature set. And for all those sets, returns a simHash list.
        
    	simHashList = []
    	i = 1
    	for f in files:
    		g = self.get_Graph(f)
    		featureSet = self.get_FeatureSet(g)
    		simHashList.append(self.get_SimHash(featureSet))
    		i += 1
    	return simHashList
    
    def get_Graph(self, f):
        # Description: Create a graph for every file in the given dataset. The graphs are directed.
    	
    	graph = nx.DiGraph()
    	graph_file = open(f,'r')
                
        # For every line in the input file, add a directed edge in the graph
    	graph.clear()
    	for line in graph_file:
    	    n1,n2 = [int(x) for x in line.split(' ')]
            graph.add_edge(n1,n2)
    	graph_file.close()
    	return graph
    
    def get_FeatureSet(self, g):
        # Description: Get a weighted feature list for every file
        # Weight of an edge (u, v) = page_rank/out_degree
        
    	page_rank = nx.pagerank(g)
    	vertexSet = [(str(ti),wi) for ti,wi in enumerate(page_rank)]
    	
    	edgeSet = []
    	for edge in g.edges():
    		(u, v) = edge
    		ti = str(u)+' '+str(v)
    		wi = page_rank[u]/g.out_degree(u)
    		edgeSet.append((ti, wi))
    		
    	return vertexSet + edgeSet
      
    def get_SimHash(self, featureSet):
        # Description: Returns simHash with respect tp feature set
    	
        b = 128
    	h = [0]*b
    	
    	for ti, wi in featureSet:
    		hex_dig = hashlib.md5(ti.encode('utf-8')).hexdigest() 
    		binary_dig = bin(int(hex_dig, 16))[2:].zfill(b)
    		for i in range(b):
   				if binary_dig[i] == '1':
					h[i] += wi
                else:
					h[i] -= wi
    			
    	for i in range(b):
    		h[i] = 1 if h[i] > 0 else 0
    	return h		
      
    def get_Similarity(self, x, y):
        # Description: Return hamming distance based similarity between two simHash vectors
        
        b, hf = len(x), 0
        for i in range(b):
            if x[i] != y[i]: 
            	hf += 1 
        return(1 - float(hf)/b)
    
    def get_Threshold(self, similarities):
        # Description: Get a threshold to identify anomalies. Returns median(to calculate distance of an anomaly) and lower bound(to check for anomaly)
        
        m, n = median(similarities), len(similarities)
        if n < 2: return(m)
        
        mr_sum = 0
        for i in range(1,n):
            mr_sum += abs(similarities[i] - similarities[i-1])
        mr = float(mr_sum)/(n-1)
    
        return m, m - 3*mr
    
    def get_Anomalies(self, simList, lowThreshold, med):
        # Description: Outputs anomalies with respect to threshold
        
        anomalies = [] 
        for idx, sim in enumerate(simList[:-1]):
            if ((sim < lowThreshold and simList[idx + 1] < lowThreshold)):
                # Get distance from median
                d = abs(sim - med)
                anomalies.append((idx + 1, d))
        return(anomalies)
    
    def get_Visualization(self, simList, lowThreshold, filename):
        # Description: Create a scatter plot with threshold line
        
        fig, ax = plt.subplots()
    	ax.scatter(range(0, len(simList)), simList, marker = '1', color = 'blue')
    	plt.axis([0, len(simList), min(simList)-0.02, max(simList)+0.02]) 
    	plt.xlabel('Graph Index')
    	plt.ylabel('Similarity')
    	plt.grid(True)   
    	line1, = ax.plot([0, len(simList)], [lowThreshold, lowThreshold], 'r--', lw=1, alpha=0.75)
    	plt.legend([line1], ['Threshold: (Median - 3 * MR)'])
    	plt.savefig(filename)
        
    def get_Output(self, anomalies, outputFile):
        # Description: Create a text file having anomalies sorted in descending order of distance from median
       
        numAnomalies = len(anomalies)
        out_file = open(outputFile , 'w+') 
        out_file.write("Number of Anomalies for are: " + str(numAnomalies))
        anomalies.sort(key= lambda item: item[1], reverse = True)
    
        for i in range(numAnomalies):
            out_file.write( '\n' + str(i+1) + ": " + str(anomalies[i][0]))
    
        out_file.close()

#----------main----------

# Create object
anomalyObj = Anomaly()

# Get all files from specified directory
if(len(sys.argv) != 2):
    print("Enter path to datasets")
    exit()
dataSet = str(sys.argv[1])
files = anomalyObj.get_FileList(dataSet)

# Calculate similarity
signatureList = anomalyObj.get_SimHashList(files)

# Calculate similarity between adjacent simHash vectors
simList = []
for i, j in zip(signatureList, signatureList[1:]):
	sim = anomalyObj.get_Similarity(i, j)
	simList.append(sim) 

# Calculate the threshold
med, lowThreshold = anomalyObj.get_Threshold(simList)

# Output file name
outputFile = "outputs/"
if "autonomous" in dataSet:
    outputFile = outputFile + "autonomous_"
elif "enron" in dataSet:
    outputFile = outputFile + "enron_by_day_"
elif "p2p" in dataSet:
    outputFile = outputFile + "p2p_Gnutella_"
elif "voices" in dataSet:
    outputFile = outputFile + "voices_"


# Visualizing results
anomalyObj.get_Visualization(simList, lowThreshold, outputFile + "plot.png")

# Get anomalies using similarity and threshold
anomalies = anomalyObj.get_Anomalies(simList, lowThreshold, med)

# Write the output in a text file
anomalyObj.get_Output(anomalies, outputFile + "time_series.txt")
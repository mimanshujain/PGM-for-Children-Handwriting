import os, sys
from os.path import isfile, join
import numpy as np
import scipy.stats

path = "/home/sherlock/Dropbox/SecondSem/AML/PGM-for-Children-Handwriting/andresultsTXTfiles";
dirs = os.listdir(path);
diction_h ={'dummy':[]};
diction_c ={'dummy':[]};
cursiveCount = 0;
hadprintCounnt = 0;
#valuesListCursivne = [];
#valuesListHandprint = [];
#indexCursiveBadRecord = [];
#indexHandprintBadRecord = [];
for year in dirs:
	hand_type =  os.listdir(path+"/"+year);
	for h_type in hand_type:
		grade = os.listdir(path+"/"+year+"/"+h_type);
		for g in grade:
			files =  os.listdir(path+"/"+year+"/"+h_type+"/"+g);
			for f in files:
				with open(path+"/"+year+"/"+h_type+"/"+g+"/"+f) as input:
   					 for line in input:
						line = line[:line.rfind(',')];
						val = line.split(',');
						if(len(val) >12):
							name = val[0].split(' ')[0];
							name = name.replace("11-12","").replace("12-13","").replace("13-14","").replace("-","");
							t = val[0][val[0].rfind(' '):].strip();
							if(t!="cursive" and t!="c" and t!="printing" and t!="p"):
								if(h_type=="cursive"):
									t = "cursive";
								else:
									t = "printing";
								
#							v = t+" "+g.replace(" ","")+" "+" ".join(val[-12:]);
                                                        v = val[-12:];
                                                        v=[x.strip() for x in v];
                                                        v=[int(x) for x in v]
							if(t!="cursive" and t!="c"):
								#v = "printing"+" "+g.replace(" ","")+" "+" ".join(val[-12:]);
								if(diction_h.has_key(g)):
									l = diction_h.get(g);
									l.append(v);
									diction_h.update({g:l})
								else:
									l=[v];
									diction_h.update({g: l})
							elif(t=="cursive" or t=="c"):	
								#v = "cursive"+" "+g.replace(" ","")+" "+" ".join(val[-12:]);
								if(diction_c.has_key(g)):
									l = diction_c.get(g);
									l.append(v);
									diction_c.update({g:l})
								else:
									l=[v];
									diction_c.update({g: l})


diction_c.pop('dummy',None);
diction_h.pop('dummy',None);


for x in diction_h:
    l = len(diction_h[x])
    a = np.zeros(shape=(6,6))
    for i in range(1,2):
        maxRow = 0
        maxCol = 0
        for j in range(0,l):
            #Finding Indexes
            i1 = diction_h[x][j][i-1]
            i2 = diction_h[x][j][i]
            #Will remove this part
            if i1 == 99 or i1 == -1 or i1 == 5:
                i1 = 1
            if i2 == 99 or i2 == -1 or i2 == 5:
                i2 = 1
            #Finding the max values
            if maxRow < i1:
                maxRow = i1
            if maxCol < i2:
                maxCol = i2
            a[i1][i2] = a[i1][i2] + 1         
        
        colSum = np.sum(a, axis=0)
        rowSum = np.sum(a, axis=1)
        total = np.sum(colSum)
        exp = np.zeros(shape=(maxRow+1,maxCol+1))
        obs = np.zeros(shape=(maxRow+1,maxCol+1))
        for k in range(0,maxRow+1):
            for j in range(0,maxCol+1):
               obs[k][j] = a[k][j]
               exp[k][j] = (colSum[j]*rowSum[k])/total
        chi = scipy.stats.chisquare(obs,exp)    
    break
print(chi)
print(exp)
'''
print(obs)        
print(colSum)
print(rowSum)   
print(exp)    ''' 


 

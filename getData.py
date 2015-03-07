import os, sys
from os.path import isfile, join
import numpy as np
#import scipy.stats
import pickle
import operator
from scipy import stats
currPath = os.path.dirname(__file__)

path = currPath + "/andresultsTXTfiles"
#path = "/home/bikramka/Downloads/andresultsTXTfiles";
#path = "/home/sherlock/Dropbox/SecondSem/AML/PGM-for-Children-Handwriting/andresultsTXTfiles";
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

#print(diction_c['grade 3'][2][1]);

#for key in 
for key in diction_h:
    #print key;
    data = np.array(diction_h[key]);
    for cIndex in range(0,12):
        mask=np.all([data[:,cIndex] != 99 , data[:,cIndex] != -1],axis = 0);
        md = int(stats.mode(data[mask,cIndex])[0][0]);
        data[np.invert(mask),cIndex] = md
    diction_h[key] =data;
for key in diction_c:
    #print key;
    data = np.array(diction_c[key]);
    for cIndex in range(0,12):
        mask=np.all([data[:,cIndex] != 99 , data[:,cIndex] != -1],axis = 0);
        md = int(stats.mode(data[mask,cIndex])[0][0]);
        data[np.invert(mask),cIndex] = md
    diction_c[key] = data;    


chi_map = {}

grade_map = {}
#grade_marg_map = {}
for key in diction_h:
    #Num of rows for that Grade
    l = len(diction_h[key])
    #Initializes the array (Max domain val of a Variable is 5)
    a = np.zeros(shape=(6,6))
    #lowMargMap = {}
    for i in range(1,12):           
        count = 1    
        for y in range(0,i):
            #marg_map = {} 
            maxRow = 0
            maxCol = 0
            for j in range(0,l):
                #Finding Indexes
                i1 = diction_h[key][j][y]
                i2 = diction_h[key][j][i]
                
                #calculate the marginal prob
                #if count == 1:
                    #if marg_map.has_key(i2):
                    #    val = marg_map.get(i2)
                    #    val = val + 1
                    #    marg_map.update({i2:val})
                    #else:
                    #    marg_map[i2] = 1
                        
                
                #Will remove this part
                if i1 == 99 or i1 == -1:
                    i1 = 1
                if i2 == 99 or i2 == -1:
                    i2 = 1
                
                #Finding the max values
                if maxRow < i1:
                    maxRow = i1
                if maxCol < i2:
                    maxCol = i2
                a[i1][i2] = a[i1][i2] + 1         
            
            #out j loop                
            colSum = np.sum(a, axis=0)
            rowSum = np.sum(a, axis=1)
            total = np.sum(colSum)
            exp = np.zeros(shape=(maxRow+1,maxCol+1))
            obs = np.zeros(shape=(maxRow+1,maxCol+1))
            
            for k in range(0,maxRow+1):
                for r in range(0,maxCol+1):
                    if a[k][r] == 0:
                        obs[k][r] = 1
                    else:
                        obs[k][r] = a[k][r]
                        
                    if colSum[r] == 0:
                        colSum[r] = maxRow
                    if rowSum[k] == 0:
                        rowSum[k] = maxCol
                        
                    exp[k][r] = (colSum[r]*rowSum[k])/total
            
            c = np.square(np.array(obs)-np.array(exp))/exp
            chi = np.sum(c)
            chi_map[str(y) + "-" + str(i)] = chi   
            #count = count + 1
        #out y loop  
        #lowMargMap[i] = marg_map
        
    #out i loop     
    
    #Normalization of Marginal Probs
    #for x in lowMargMap:
    #    sum_i = 0
    #    for z in lowMargMap[x]:
    #       sum_i = sum_i + lowMargMap[x][z]
    #    for z in lowMargMap[x]:
    #        lowMargMap.update({z:lowMargMap[x][z]/sum_i})
            
    #grade_marg_map[key] =  lowMargMap 
    grade_map[key] = chi_map  
        
sor_map = {}    
for k in grade_map:
    sorted_x = sorted(grade_map[k].items(), key=operator.itemgetter(1))   
    sor_map[k] = sorted_x

                                        
##sorted_x = sorted(chi_map.items(), key=operator.itemgetter(1))
#pickle.dump(sor_map, open( currPath+"/chiValues.p", "wb" ) )
#print(len(sor_map))
#for k in sor_map:
#    print(k)
#    #print(len(sor_map[k]))
##
##print(obs)  
##print(exp) 
#'''
#print(colSum)
#print(rowSum)   
#print(exp)    ''' 
marginal = dict()
grade_marginal = dict()
for key in diction_h:
    dat=diction_h[key];
    for i in range(0,12):
        marginal_table = stats.itemfreq(dat[:,i])
        marginal_table_values = marginal_table[:,1]
        s = len(dat)
        s = np.double(s);
        
        marginal_table_values = marginal_table_values/s;
       # print marginal_table_value;
        for j in range(0, len(marginal_table_values)):
            print j
            marginal_table[j,1] = marginal_table_values[j];
        marginal[i] = marginal_table
    grade_marginal[key] = marginal     

                 
#sorted_x = sorted(chi_map.items(), key=operator.itemgetter(1))
pickle.dump(sor_map, open( currPath+"/chiValues.p", "wb" ) )
#print(len(sor_map))
adj_map = dict();
for k in sor_map:
    c_m = sor_map[k];
    c_m = c_m[-15:];
    adj_mat = np.zeros((12,12),dtype = np.int);
    for t in c_m:
        ijs = t[0].split('-');
        i = int(ijs[0]);
        j = int(ijs[1]);
        adj_mat[i][j] = np.int(1);
        adj_mat[j][i] = np.int(1);
    #print(adj_mat);
    adj_map[k] = adj_mat;
    
    
    
#
#print(obs)  
#print(exp) 
'''
print(colSum)
print(rowSum)   
print(exp)    ''' 


    

 

#for key in grade_ma    


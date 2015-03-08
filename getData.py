import os, sys
from os.path import isfile, join
import numpy as np
#import scipy.stats
import pickle
import operator
from scipy import stats
currPath = os.path.dirname(__file__)

#Joint prob with dictionary as output like 0,0 or 0,1

conditionals_g = dict()
def calculateJoin(grade_marginal, Xi, Xj, key):
    iMarginal = grade_marginal[key][Xi];
    jMarginal = grade_marginal[key][Xj];
    cond = dict();
    for iIndex in iMarginal:
        #iIndexInt = int(iIndex);
        for jIndex in jMarginal:
           # jIndexInt = int(jIndex)
            k1 = str(iIndex) + ',' + str(jIndex)
            cond[k1] = iMarginal[iIndex]*jMarginal[jIndex]
            
    return cond

#Joint prob with direct Marginal with output as dictionary        
def calculateJoinMarginal(marginal1, marginal2):
    iMarginal = marginal1;
    jMarginal = marginal2;
    cond = dict();
    for iIndex in iMarginal:
        #iIndexInt = int(iIndex);
        for jIndex in jMarginal:
           # jIndexInt = int(jIndex)
            k1 = str(iIndex) + ',' + str(jIndex)
            cond[k1] = iMarginal[iIndex]*jMarginal[jIndex]
            
    return cond
    
def calculateAdj(sor_map):
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
    return adj_map;

def calculateConditional(marginal, given):
    iMarginal = marginal;
    jMarginal = given;
    cond = dict();
    for iIndex in iMarginal:
        #iIndexInt = int(iIndex);
        for jIndex in jMarginal:
           # jIndexInt = int(jIndex)
            k1 = str(iIndex) + '|' + str(jIndex)
            cond[k1] = iMarginal[iIndex]*jMarginal[jIndex]
    for key in cond:
        key = str(key);
        givenValueKey = key.split('|')[1];
        #if givenValueKey not in given:
        #    print("aa")
        givenValue = given[givenValueKey];
        cond[key] = cond[key]/givenValue;
            
    return cond

path = currPath + "/andresultsTXTfiles"
#path = "/home/bikramka/Downloads/andresultsTXTfiles";

    
def calculateConditionalQuery(query, grade_marginal, key):
    global conditionals_g;
    if query in conditionals_g:
        return conditionals_g[query]
    values = query.split('|');
    givens = values[1].split(',');
    if len(givens) == 1:
        cond = calculateConditional(grade_marginal[key][values[0]],grade_marginal[key][givens[0]]);
    else:
        cond = grade_marginal[key][0]
        for i in range(1, len(givens)):
            cond = calculateJoinMarginal(cond, grade_marginal[key][i])
        cond = calculateConditional(grade_marginal[key][int(values[0])], cond);
    conditionals_g[query] = cond;
    return cond;
    
def calcConditionalValues(cond, valueQuery):
    returnValue = cond[valueQuery];
    return returnValue;
            
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
    for i in range(1,12):           
        count = 1    
        for y in range(0,i):
            maxRow = 0
            maxCol = 0
            for j in range(0,l):
                #Finding Indexes
                i1 = diction_h[key][j][y]
                i2 = diction_h[key][j][i]
                        
                
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
    grade_map[key] = chi_map  

#sorting the Chi Square values                
sor_map = {}    
for k in grade_map:
    sorted_x = sorted(grade_map[k].items(), key=operator.itemgetter(1))   
    sor_map[k] = sorted_x

#Calculating Marginal Prob                                                                        
grade_marginal = dict()
for key in diction_h:
    marginal = dict()
    dat=diction_h[key];
    for i in range(0,12):
        marginal_table = stats.itemfreq(dat[:,i])
        marginal_table_values = marginal_table[:,1]
        s = len(dat)
        s = np.double(s);
        
        marginal_table_values = marginal_table_values/s;
        marginal_table1 = dict();
       # print marginal_table_value;
        for j in range(0, len(marginal_table_values)):
            marginal_table[j,1] = marginal_table_values[j];
            marginal[i] = marginal_table
            marginal_table1[j,0] = marginal_table[j,0]
            marginal_table1[j,1] = np.double(marginal_table_values[j]);

            jk = str(marginal_table[j,0]);
            marginal_table1[jk] = np.double(marginal_table_values[j]);
            #marginal_table1[j,1] = np.double(marginal_table_values[j]);

        marginal[i] = marginal_table1
    grade_marginal[key] = marginal     

pickle.dump(sor_map, open( currPath+"/chiValues.p", "wb" ) )

#print(len(sor_map))
adj_map = calculateAdj(sor_map);
    
#code for joint probabilities
conditionals = dict()
#grade is key
#value: list of tuple('Xi|Xj', condMap)
for key in adj_map:
    #print k;
    for i in range(0,12):
        for j in range(0,12):
            if adj_map[key][i][j] == 1:
                #cond = calculateConditional(grade_marginal[key][i],grade_marginal[key][j])
                cond = calculateConditional(grade_marginal[key][i],grade_marginal[key][j])
        k = str(i)+'|'+str(j)
        if key in conditionals:
            conditionals[key][k] = cond;
        else:
            conditionals[key] = {k:cond};
    
G = np.zeros((12,12),dtype = np.int);

def calculateScore(G_star, key, l, ):
    biggerSum = 0.0
    for i in range(0,l):
        smallerSum = 0.0
        for j in range(0,12):                                    
            parents = G_star[key][j]
            if len(parents) > 0:
                probKey = ""
                valueQuery = ""
                for par in range(0,len(parents)):
                    if parents[par] == 1:
                        if probKey == "":
                            probKey = str(par)
                            valueQuery = str(diction_h[key][i][par])
                        else:
                            probKey = probKey + "," + str(par);
                            valueQuery = valueQuery + "," + str(diction_h[key][i][par])
                            
                probKey = str(j)+"|"+probKey
                valueQuery = str(diction_h[key][i][j]) + "|" + valueQuery
                cond = calculateConditionalQuery(probKey, grade_marginal, key)                
                smallerSum = smallerSum + cond[valueQuery]
            else:
                smallerSum = smallerSum + grade_marginal[key][j].get(diction_h[key][i][j])
        #End of j loop
        biggerSum = biggerSum + smallerSum  
    return biggerSum
    
for key in sor_map:
    d_m = sor_map[key];
    d_m = d_m[-15:];    
    for t in d_m:
        ijs = t[0].split('-');    
        vertex1 = int(ijs[0]);
        vertex2 = int(ijs[1]);
        l = len(diction_h[key])
        
        G_star1 = G
        G_star2 = G
        G_star1[vertex1] = 1 #Vertex 2 is the parent       
        G_star1[vertex2] = 1 #Vertex 1 is the parent       
        sum1 = calculateScore(G_star1, key, l)  
        sum2 = calculateScore(G_star2, key, l)       
        
        sum1 = -np.log(sum1)
        sum2 = -np.log(sum2)
        
        if sum1 < sum2:
            G = G_star1
        #End of i loop
     #End of t loop                                       
#End of Key loop


calculateConditionalQuery('1|2,11', grade_marginal, 'grade 2');

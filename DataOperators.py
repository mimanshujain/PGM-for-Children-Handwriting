__author__ = 'sherlock'
import os
import numpy as np
import pickle
import operator
import igraph as ig
from scipy import stats
from getVariableDomain import getHandPrintDomain

graphMaker = ig.Graph()

currPath = os.path.dirname(__file__)

path = currPath + "/andresultsTXTfiles"

def getData(type):
    dirs = os.listdir(path)
    diction ={'dummy':[]}

    for year in dirs:
        gradesPath = path + "/" + year + "/" +type
        if os.path.exists(gradesPath):
            grade = os.listdir(gradesPath)
            for g in grade:
                gradePath = gradesPath + "/"+g
                files =  os.listdir(gradePath)
                for f in files:
                    with open(gradePath+"/"+f) as inp:
                        for line in inp:
                            line = line[:line.rfind(',')]
                            val = line.split(',')
                            if len(val) > 12:
                                v = val[-12:]
                                v = [x.strip() for x in v]
                                v = [int(x) for x in v]

                                if diction.has_key(g):
                                    featureList = diction.get(g)
                                    featureList.append(v)
                                    diction.update({g: featureList})
                                else:
                                    featureList = [v]
                                    diction.update({g: featureList})

    diction.pop('dummy', None)

    return diction

def missingValueInputation(diction):
    for key in diction:
        data = np.array(diction[key])
        for cIndex in range(0,12):
            mask = np.all([data[:, cIndex] != 99 , data[:, cIndex] != -1, data[:, cIndex] != 5], axis = 0)
            md = int(stats.mode(data[mask,cIndex])[0][0])
            data[np.invert(mask), cIndex] = md
        diction[key] = data

    return diction

def getChiSquareValue(diction):
    grade_map = {}
    for key in diction:
        chi_map = {}
        #Num of rows for that Grade
        l = len(diction[key])
        #Initializes the array (Max domain val of a Variable is 5)
        a = np.zeros(shape=(6,6))
        for i in range(1, 12):
            for y in range(0,i):
                maxRow = 0
                maxCol = 0
                for j in range(0,l):
                    #Finding Indexes
                    i1 = diction[key][j][y]
                    i2 = diction[key][j][i]

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

    pickle.dump(sor_map, open( currPath+"/chiValues.p", "wb"))
    return sor_map

def getMarginalProb(diction):
    grade_marginal = dict()
    lst = getHandPrintDomain()
    for key in diction:
        marginal = dict()
        dat= diction[key]
        for i in range(0,12):
            marginal_table = stats.itemfreq(dat[:,i])
            if key == 'grade 2' and i == 0:
                print
            marginalTemplate = dict(lst[i])
            for templateValue in marginal_table[:,0]:
                marginalTemplate.pop(templateValue, None)
            for templateKey in marginalTemplate:
                marginal_table = np.append(marginal_table, [[templateKey, 1]], axis = 0)
            marginal_table_values = marginal_table[:,1]
            s = len(dat)
            s = np.double(s)

            marginal_table_values = marginal_table_values/s
            marginal_table1 = dict()
           # print marginal_table_value
            for j in range(0, len(marginal_table_values)):
                marginal_table[j,1] = marginal_table_values[j]

                jk = str(marginal_table[j,0])
                if len(jk) > 1:
                    print
                marginal_table1[jk] = np.double(marginal_table_values[j])

            marginal[i] = marginal_table1
        grade_marginal[key] = marginal


    return grade_marginal

def calculateAdj(sor_map):
    adj_map = dict()
    for k in sor_map:
        c_m = sor_map[k]
        c_m = c_m[-15:]
        adj_mat = np.zeros((12,12), dtype = np.int)
        for t in c_m:
            ijs = t[0].split('-')
            i = int(ijs[0])
            j = int(ijs[1])
            adj_mat[i][j] = np.int(1)
            adj_mat[j][i] = np.int(1)
        adj_map[k] = adj_mat
    return adj_map

def calculateConditional(marginal, given):
    iMarginal = marginal
    jMarginal = given
    cond = dict()
    for iIndex in iMarginal:
        #iIndexInt = int(iIndex)
        for jIndex in jMarginal:
           # jIndexInt = int(jIndex)
            k1 = str(iIndex) + '|' + str(jIndex)
            cond[k1] = iMarginal[iIndex]*jMarginal[jIndex]
            if int(jMarginal[jIndex]) == 3:
                print("stop")
    for key in cond:
        key = str(key)
        givenValueKey = key.split('|')[1]
        #if givenValueKey not in given:
        #    print("aa")
        givenValue = given[givenValueKey]
        cond[key] = cond[key]/givenValue

    return cond

def calculateJoinMarginal(marginal1, marginal2):
    iMarginal = marginal1
    jMarginal = marginal2
    cond = dict()
    for iIndex in iMarginal:
        #iIndexInt = int(iIndex)
        for jIndex in jMarginal:
           # jIndexInt = int(jIndex)
            k1 = str(iIndex) + ',' + str(jIndex)
            cond[k1] = iMarginal[iIndex]*jMarginal[jIndex]

    return cond

conditionals_g = dict()
def calculateConditionalQuery(query, grade_marginal, key):
    global conditionals_g
    if query in conditionals_g:
        return conditionals_g[query]
    values = query.split('|')
    if len(values) == 1:
        return grade_marginal[key][int(values[0])]
    givens = values[1].split(',')
    if len(givens) == 1:
        if int(givens[0]) == 10 & int(values[0]) == 1:
            print("stop")
        cond = calculateConditional(grade_marginal[key][int(values[0])],grade_marginal[key][int(givens[0])])
    else:
        cond = grade_marginal[key][int(givens[0])]

        for i in range(1, len(givens)):
            cond = calculateJoinMarginal(cond, grade_marginal[key][int(givens[i])])
        cond = calculateConditional(grade_marginal[key][int(values[0])], cond)
    conditionals_g[query] = cond
    return cond

def calculateScore(G_star, key, l, diction, grade_marginal):
    biggerSum = 0.0
    for i in range(0,l):
        smallerSum = 0
        for j in range(0,12):                                    
            parents = G_star[j]
            if len(parents) > 0:
                probKey = ""
                valueQuery = ""
                if sum(parents) > 0:
                    for par in range(0,len(parents)):
                        if parents[par] == 1:
                            if probKey == "":
                                probKey = str(par)
                                valueQuery = str(diction[key][i][par])
                            else:
                                probKey = probKey + "," + str(par)
                                valueQuery = valueQuery + "," + str(diction[key][i][par])
                    
                if probKey == "":  
                    probKey = str(j)
                    valueQuery = str(diction[key][i][j])
                else:          
                    probKey = str(j)+"|"+probKey
                    valueQuery = str(diction[key][i][j]) + "|" + valueQuery
                if probKey == "1|10":
                    if valueQuery == "1|3":
                        print(key)
                        print("Stop")
                        cond = calculateConditionalQuery(probKey, grade_marginal, key)
                        print(cond)
                cond = calculateConditionalQuery(probKey, grade_marginal, key)                
                smallerSum = smallerSum + cond[valueQuery]
            else:
                smallerSum = smallerSum + grade_marginal[key][j].get(diction[key][i][j])
        #End of j loop
        biggerSum = biggerSum + smallerSum  
    return biggerSum

def generateNetwork(sor_map, diction, grade_marginal):
    gradeGraph = dict()
    for key in sor_map:
        G = np.zeros((12,12),dtype = np.int)
        d_m = sor_map[key]
        d_m = d_m[-20:]
        for t in d_m:
            ijs = t[0].split('-')
            vertex1 = int(ijs[0])
            vertex2 = int(ijs[1])
            l = len(diction[key])

            G_star1 = np.array(G)
            G_star2 = np.array(G)
            G_star1[vertex1][vertex2] = 1 #Vertex 2 is the parent
            G_star2[vertex2][vertex1] = 1 #Vertex 1 is the parent
            sum1 = 0
            sum2 = 0
            g1 = graphMaker.Adjacency(G_star1.tolist())
            g2 = graphMaker.Adjacency(G_star2.tolist())

            if g1.is_dag():
                sum1 = calculateScore(G_star1, key, l, diction, grade_marginal)
                sum1 = -np.log(sum1)
            if g2.is_dag():
                sum2 = calculateScore(G_star2, key, l, diction, grade_marginal)
                sum2 = -np.log(sum2)


            if sum1 < sum2:
                G = G_star1
            elif sum1 != 0 and sum2 != 0:
                G = G_star2

            #End of i loop
         #End of t loop
        gradeGraph[key] = G

    return gradeGraph
    #End of Key loop

def meanOfDistribution(diction):
    meanDistr = dict()
    for key in diction:
        meanSmall = dict()
        l = len(diction[key])
        for i in range(0,12):
            meanSmall[i] = diction[key][:,i].sum()
            meanSmall[i] = meanSmall[i]/l
        meanDistr[key] = meanSmall

    return meanDistr





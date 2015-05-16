import DataOperators

diction_c = dict()
diction_h = dict()

if __name__ == '__main__':
    handPrint = "handprint"
    cursive = "cursive"
    diction_h = DataOperators.getData(handPrint)
    diction_c = DataOperators.getData(cursive)

    diction_h = DataOperators.missingValueInputation(diction_h)
    diction_c = DataOperators.missingValueInputation(diction_c)

    gradeMap_h = DataOperators.getChiSquareValue(diction_h)
    gradeMap_c = DataOperators.getChiSquareValue(diction_c)

    grade_marginal_h = DataOperators.getMarginalProb(diction_h)
    grade_marginal_c = DataOperators.getMarginalProb(diction_c)

    adjacency_h = DataOperators.calculateAdj(gradeMap_h)
    adjacency_c = DataOperators.calculateAdj(gradeMap_c)

    graphMat_h = DataOperators.generateNetwork(gradeMap_h, diction_h, grade_marginal_h)
    graphMat_c = DataOperators.generateNetwork(gradeMap_c, diction_c, grade_marginal_c)

    mean_h = DataOperators.meanOfDistribution(diction_h)
    mean_c = DataOperators.meanOfDistribution(diction_c)
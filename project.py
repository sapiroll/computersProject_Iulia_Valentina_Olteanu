import matplotlib.pyplot as matp
import numpy as nump


def fit_linear(filename):
    file = open(filename)
    data = file.readlines()
    data = match(data)
    nump = ""
    ran = []
    ran = isValid(data[0][0], data[0][1], data[0][2], data[0][3])
    if ran == None:
        return
    xData = ran[0];
    dx = ran[1]; yData = ran[2]; dy = ran[3];
    info_x = data[1]
    info_y = data[2]
    info_x, info_y = axis(info_x, info_y)
    a, b = avg_for_all(xData, yData, dy, dx)
    matp.clf()
    matp.plot(xData, yData, 'ro', color='blue',markersize='1.3')
    matp.plot([min(xData), max(xData)], [a*min(xData)+b, a*max(xData)+b], color='red')
    matp.xlabel(info_x)
    matp.ylabel(info_y)
    matp.errorbar(xData, yData, xerr=dx, yerr=dy, ecolor='blue', fmt='None')
    matp.savefig("linear_fig.SVG")
    file.close()
    return


def isValid(xData, dx, yData, dy): # checking for errors in the data
    if len(xData) != len(dx) or len(xData) != len(yData) or len(yData) != len(dy):
        print('Input file error: Data lists are not the same length')
        return
    else:
        for v in dx:
            if v <= 0:
                print('Input file error: Not all uncertainties are positive')
                return
        for v in dy:
            if v <= 0:
                print('Input file error: Not all uncertainties are positive')
                return
    ran = [xData, dx, yData, dy]
    return ran


# organized the data
def match(info):
    info_x = None
    info_y = None
    p = []
    min_ = 0; mid_ = 0; max_ = 0;
    _a_b = [[0, 0, 0], [0, 0, 0]]
    before = [] 
    xo = False
    xoxo = False
    for line in info:
        line.replace('\n', ' ')
        modify = line.strip().split(' ')
        if 'axis:' in modify and 'x' in modify:
            info_x = (modify[2:])
        elif 'axis:' in modify and 'y' in modify:
            info_y = (modify[2:])
        elif 'a' in modify:
            _a_b[0] = new_(modify[1:])
            xo = True
        elif 'b' in modify:
            _a_b[1] = new_(modify[1:])
            xoxo = True
        else:
            if len(modify) > 0:
                if modify[0] != '':
                    before.append(modify)
    # # before.remove([''])
    dat = []
    T = [] 
    low_case = None
    for l in before:  # l = 'list', i = 'item'
        T = []
        low_case = None
        for i in l:
            low_case = i.lower()
            T.append(low_case)
        try:
            T.remove('')
            dat.append(T)
        except:
            dat.append(T)
    name_axis = ['x', 'dx', 'y', 'dy'] 
    after_data = [] 
    T = []
    strings = [] 
    if dat[0][1] in name_axis and dat[0][0] in name_axis: # when data is sorted in columns
        for name in name_axis: 
            T = []
            r = 999
            if name in dat[0]:
                r = dat[0].index(name) # place of name in dat
                for i in range(1, len(dat)):
                    try:
                        T.append(float(dat[i][r]))
                    except:
                        continue
            after_data.append(T)
    else: # when data is sorted in rows
        for name in name_axis:
            strings = None
            for l in dat:
                T = []
                if l[0] == name:
                    for i in l[1:]:
                        T.append(float(i))
                    after_data.append(T)
    answer = [after_data, info_x, info_y]
    if xo and xoxo:
        find_a_b_best(answer, _a_b)
    return answer


def avg_for_all(xData, yData, dy, dx):
    x = xData
    y = yData
    b_1divdy2 = []  # inicial 1/dy^2
    dy2 = []  # dy squart
    # build a list 1/dy^2
    for num in dy:
        b_1divdy2.append(1 / num ** 2)
        dy2.append(num ** 2)
    one_divid_dy2 = sum(b_1divdy2)

    # build a list of x^2
    x2 = []  # x squart
    for num in x:
        x2.append(num ** 2)
    xy = []
    # build list of x*y
    for i in range(0, len(x)):
        xy.append(x[i] * y[i])
    x_up = 0
    y_up = 0
    xy_up = 0
    x2_up = 0
    dy2_up = 0
    for i in range(len(x)):  # calculates the sum of all the upper values in the avg
        x_up = x_up + x[i] * b_1divdy2[i]
        y_up = y_up + y[i] * b_1divdy2[i]
        xy_up = xy_up + xy[i] * b_1divdy2[i]
        x2_up = x2_up + x2[i] * b_1divdy2[i]
        dy2_up = dy2_up + dy2[i] * b_1divdy2[i]

    x_avg_fin = (x_up / one_divid_dy2)
    y_avg_fin = (y_up / one_divid_dy2)
    dy2_avg_fin = (dy2_up / one_divid_dy2)
    x2_avg_fin = (x2_up / one_divid_dy2)
    xy_avg_fin = (xy_up / one_divid_dy2)
    a = (xy_avg_fin - (x_avg_fin * y_avg_fin)) / (x2_avg_fin - (x_avg_fin ** 2))
    da = (dy2_avg_fin / (len(x)*(x2_avg_fin - (x_avg_fin**2)))) ** 0.5
    b = y_avg_fin - (a * x_avg_fin)
    db = ((dy2_avg_fin * x2_avg_fin) / (len(dy)*(x2_avg_fin - (x_avg_fin**2)))) ** 0.5
    x_notred = 0
    for i in range(len(x)):
        k = y[i] - (a * x[i] + b)
        z = (k / dy[i]) ** 2
        x_notred = x_notred + z
    x_red = (x_notred / (len(dy) - 2))
    _a_b = [[]]
    print("a=", a, "+-", da)
    print("b=", b, "+-", db)
    print("chi2=", x_notred)
    print("chi2_reduced=", x_red)
    return a, b


def new_(modify):
    p = []
    b = []
    min_ = modify[0]
    max_ = modify[0]
    for a in modify:
        if abs(float(a)) < abs(float(min_)):
            min_ = a
        if float(a) > float(max_):
            max_ = a
    b = [min_, max_]
    for a in modify:
        if a not in b:
            p.append(float(a))
    p.append(float(max_));p.append(float(min_));
    return p


def axis(x_axis, y_axis):
    x_initial = ''
    for i in range(0, len(x_axis)):
        x_initial = x_initial + ' ' + x_axis[i]
    x_axis_fin = x_initial.strip()
    y_initial = ''
    for i in range(0, len(y_axis)):
        y_initial = y_initial + " " + y_axis[i]
    y_axis_fin = y_initial.strip()
    return(x_axis_fin,y_axis_fin)


#the bonus part
from math import sqrt
def find_a_b_best(answer,_a_b):
    lol=0
    for n in nump.arange(1, len(answer[0][0])):
        lol = lol + ((answer[0][2][n] - (_a_b[0][0] * answer[0][1][n] + _a_b[1][0] )) / (ans[0][3][n])) ** 2
    x_min = lol
    a_fin=0
    b_fin=0
    for a in nump.arange(_a_b[0][0], _a_b[0][1], _a_b[0][2]):
        for b in nump.arange(_a_b[1][0] + 1, _a_b[1][1], _a_b[1][2]):
            check=0
            sum=0
            for n in nump.arange(0,len(answer[0][0])):
                sum=((answer[0][2][n]-(a*answer[0][1][n]+b))/(answer[0][3][n]))**2
                check+=sum
            if (check<x_min):
                x_min=check
                a_fin=a
                b_fin=b
    x_min_red=x_min/sqrt(len(answer[0][0]))
    print("a=", a_fin, "+-", _a_b[0][2])
    print("b=", b_fin, "+-", _a_b[1][2])
    print("chi2=", x_min)
    print("chi2_reduced=", x_min_red)
    aranged = [[], []]
    for a in nump.arange(_a_b[0][0], _a_b[0][1], _a_b[0][2]):
        check = 0
        sum=0
        for n in range(0, len(answer[0])):
            sum = (float(answer[0][2][n]) - (float(a) * float(answer[0][1][n]) + float(b_fin))) / (float((answer[0][3][n]))) ** 2
            check += sum
        print(sum,a)
        aranged[0].append(sum)
        aranged[1].append(a)
    matp.clf()
    matp.plot(aranged[1], aranged[0], color='blue')
    matp.xlabel("A")
    matp.ylabel("Chi^2")
    matp.savefig("BestFit.SVG")


#fit_linear("InputExcemple")

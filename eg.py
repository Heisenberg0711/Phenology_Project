test_pixel = VI_imgs[0:365,idx]

Lmin_1 = test_pixel[0]
Lmin_2 = test_pixel[-1]

x = np.zeros(2)
dL_1 = test_pixel.max() - Lmin_1

y = np.zeros(2)
dL_2 = test_pixel.max() - Lmin_2
t12 = np.argmax(test_pixel)

def double_logistic_plot(x,t):
    if t <= x[4]:
        return x[5] + x[7] * sigmoid(-(x[0] - x[1] * t))
    else:
        return x[6] + x[8] * sigmoid(-(-x[2] + x[3]*(t - x[4])))

def a_logistic_plot(x,t):
    return Lmin_1 + dL_1 * sigmoid(-(x[0] - x[1] * t))

def b_logistic_plot(x,t):
    return Lmin_2 + dL_2 * sigmoid(-(-x[0] + x[1]*(t - t12)))

def Cost_a(x):
    def a_logistic(x,t):
        return Lmin_1 + dL_1 * sigmoid(-(x[0] - x[1] * t))
    time = np.arange(1,np.argmax(test_pixel)+1)
    cost = 0
    for i in time:
        out = a_logistic(x,i)
        cost += (out - test_pixel[i-1]) * (out - test_pixel[i-1])
    return cost

def Cost_b(x):
    def b_logistic(x,t):
        return Lmin_2 + dL_2 * sigmoid(-(-x[0] + x[1]*(t - t12)))
    time = np.arange(np.argmax(test_pixel)+1,366)
    cost = 0
    for i in time:
        out = b_logistic(x,i)
        cost += (out - test_pixel[i-1]) * (out - test_pixel[i-1])
    return cost


def Cost(x):
    def double_logistic(x,t):
        if t <= x[4]:
            return x[5] + x[7] * sigmoid(-(x[0] - x[1] * t))
        else:
            return x[6] + x[8] * sigmoid(-(-x[2] + x[3]*(t - x[4])))
    time = np.arange(1,366)
    cost = 0
    for i in time:
        out = double_logistic(x,i)
        cost += (out - test_pixel[i-1]) * (out - test_pixel[i-1])
    return cost

def equations_a(p):
    a_1, b_1 = p
    return ((Lmin_1 + dL_1 * sigmoid(-(a_1 - b_1 * 1)) - Lmin_1), (Lmin_1 + dL_1 * sigmoid(-(a_1 - b_1 * np.argmax(test_pixel))) - test_pixel.max()))


def equations_b(p):
    a_2, b_2 = p
    return  (Lmin_2 + dL_2 * sigmoid(-(-a_2 + b_2*(t12 + 1 - t12)))- test_pixel.max(), dL_2 * sigmoid(-(-a_2 + b_2*(365 - t12))))
def cons_f(x):
    return x[5] + x[7] * sigmoid(-(x[0] - x[1] * x[4])) - (x[6] + x[8] * sigmoid(-(-x[2])))

x[0], x[1] =  fsolve(equations_a, (0,0))
y[0], y[1] =  fsolve(equations_b, (0,0))


res_1 = minimize(Cost_a, x, method='Nelder-Mead')
res_2 = minimize(Cost_b, y, method='Nelder-Mead')

z = np.zeros(9)
z[4] = np.argmax(test_pixel) + 1
z[5] = Lmin_1
z[6] = Lmin_2
z[7] = test_pixel.max() - Lmin_1
z[8] = test_pixel.max() - Lmin_2
z[0] = res_1.x[0]
z[1] = res_1.x[1]
z[2] = res_2.x[0]
z[3] = res_2.x[1]

eq_cons = {'type': 'eq', 'fun' : lambda x: [x[7] * np.exp(x[2]) - x[8] * np.exp(x[1] * x[4] - x[0]) + x[7] - x[8]],'jac' : lambda x: np.array([x[8] * np.exp(x[1] * x[4] - x[0]), x[4] *-x[8] * np.exp(x[1] * x[4] - x[0]),x[7] * np.exp(x[2]), 0,x[1] *-x[8] * np.exp(x[1] * x[4] - x[0]),0,0,np.exp(x[2])+1,-1-np.exp(x[1] * x[4] - x[0])])}

eq_cons_1 = {'type': 'eq', 'fun' : lambda x: x[7] + x[5] - x[8] - x[6],'jac' : lambda x: np.array([0,0,0,0,0,1,-1,1,-1])}
res = minimize(Cost, z, method='SLSQP', jac = '2-point',constraints=(eq_cons,eq_cons_1),options={'maxiter':200})

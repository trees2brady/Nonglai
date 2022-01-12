import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


def saw_sift(t, y, bc='extrap', tol=0.0):
    """
    利用sawtooth变换找出数据中占主导地位的固有模式。

    参数
    ----------
    t : 1维数组
        独立数据, 长度 N.
    y : 1维数组
        独立数据, 长度 N.
    bc : {'auto'|'even'|'odd'|'periodic'|'extend'}, 可选
        extrap :
            默认. 根据需要从最后两个envelopes外推
        even :
            使用端点作为极值并反射最近的exrema来扩展相反的包络线
        odd :
           在每个端点附近反射和翻转最近的两个极值，而不使用端点作为极值(类似于以端点为原点的奇函数)来推断两个envelopes
        periodic :
            将函数(即极值)视为周期函数，以附加必要的额外极值
        tol : 浮点数的容忍度。低于此级别的点之间的更改被设置为零。

    Returns
    -------
    h : 1D 数组
        即主要模式e, 长度 N.

    ----------
    """
    t, y = map(np.asarray, [t, y])
    argext = _allrelextrema(y, tol=tol)#确定相对极值

    if len(argext) < 2:   #如果极值太少，则提出异常
        raise FlatFunction('相对max和min太少，无法筛选该序列')

    T = t[argext]    #解析出相对极值
    E = y[argext]

    if bc == 'extrap':   #为边界条件添加额外的极值
        if len(argext) < 4:
            raise FlatFunction('相对max和min太少，无法筛选该序列')
        t0, tn1 = t[0], t[0]
        E0 = (E[3] - E[1]) / (T[3] - T[1]) * (t0 - T[1]) + E[1]
        En1 = (E[2] - E[0]) / (T[2] - T[0]) * (tn1 - T[0]) + E[0]
        tmn1, tm = t[-1], t[-1]
        Emn1 = (E[-4] - E[-2]) / (T[-4] - T[-2]) * (tmn1 - T[-2]) + E[-2]
        Em = (E[-3] - E[-1]) / (T[-3] - T[-1]) * (tm - T[-1]) + E[-1]
    elif bc == 'even':
        t0, E0 = t[0], y[0]
        tn1, En1 = _reflect(t[0], T[0]), E[0]
        tmn1, Emn1 = t[-1], y[-1]
        tm, Em = _reflect(t[-1], T[-1]), E[-1]
    elif bc == 'odd':
        t0, tn1 = _reflect(t[0], T[:2])
        E0, En1 = _reflect(y[0], E[:2])
        tm, tmn1 = _reflect(t[-1], T[-2:])
        Em, Emn1 = _reflect(y[-1], E[-2:])
    elif bc == 'periodic':
        if _oppsign(y[1] - y[0], y[0] - y[-1], tol):               #左端点是一个相对极值
            t0, E0 = t[0], y[0]
            tn1, En1 = t[0] - (t[-1] - T[-1]), E[-1]
        else:                                                     #右端点是一个相对极值
            t0, E0 = t[0] - (t[-1] - T[-1]), E[-1]
            tn1, En1 = t[0] - (t[-1] - T[-2]), E[-2]
        if _oppsign(y[-1] - y[-2], y[0] - y[-1], tol):             #右端点是一个相对极值
            tmn1, Emn1 = t[-1], y[-1]
            tm, Em = t[-1] + (T[0] - t[0]), E[0]
        else:
            tmn1, Emn1 = t[-1] + (T[0] - t[0]), E[0]
            tm, Em = t[-1] + (T[1] - t[0]), E[1]
    else:
        raise ValueError('边界条件(bc)不理解！')

    N = len(T)                                                     #把边界点加到极值
    T = np.insert(T, [0, 0, N, N], [tn1, t0, tmn1, tm])
    E = np.insert(E, [0, 0, N, N], [En1, E0, Emn1, Em])
    argext = np.insert(argext, [0, 0, N, N], [0, 0, len(t), len(t)])

    Tsaw, Ysaw = T[1:-1], E[1:-1]                                  #解析saw函数和信封点
    env1 = np.interp(Tsaw, T[::2], E[::2])
    env2 = np.interp(Tsaw, T[1::2], E[1::2])

    env_mean = (env1 + env2) / 2.0                                     #从sawtooth中减去包络平均(sawtooth是极值)
    Hsaw = Ysaw - env_mean

    u = _saw_transform(t, y, T, E, argext)                            #从到数据空间的转换
    h = np.interp(u, Tsaw, Hsaw)

    return h


def _saw_transform(t, y, T, E, argext):
    """返回t坐标的sawtooth变换."""
    u = []
    for i in range(1, len(argext) - 2):
        piece = slice(argext[i], argext[i+1])
        upiece = (T[i] + (y[piece] - E[i]) / (E[i+1] - E[i])
                    * (T[i+1] - T[i]))
        u.extend(upiece)
    return np.array(u)


def saw_emd(t, y, Nmodes=None, bc='extrap', tol=1e-10):
    """
    参数
    ----------
    t : 1D 数组
        独立数据, 长度 N.
    y : 1D 数组
        独立数据, 长度 N.
    Nmodes : int, 可选
        最大返回模式数
    bc : {'auto'|'even'|'odd'|'periodic'|'extend'}, 可选
        extrap :
            默认. 根据需要从最后两个外推envelopes
        even :
            使用端点作为极值并反射最近的exrema来扩展相反的包络线
        odd :
            在每个端点附近反射和翻转最近的两个极值，而不使用端点作为极值(类似于以端点为原点的奇函数)来推断两个envelopes
        periodic :
            将函数(即极值)视为周期函数，以附加必要的额外极值
    tol : float
        相对于函数初始范围的公差。一旦y的波动低于这个水平，分解就会停止。

    Returns
    -------
    c : 2D 数组
        一个 NxM 数组可以给出 M 个经验模式作为列
    r : 1D 数组
        残余序列, 长度 N.

    ----------
    """
    t, y = map(np.asarray, [t, y])
    if t.ndim > 1:
        raise ValueError("t 数组必须是1D")
    if y.ndim > 1:
        raise ValueError("y 数组必须是1D")

    atol = tol * (np.max(y) - np.min(y))

    c = []
    r = np.copy(y)
    while True:
        try:
            h = saw_sift(t, r, bc=bc, tol=atol)
            c.append(h)
            r = r - h
        except FlatFunction:                               #如果残差的极值太少
            break
        if len(c) == Nmodes:
            break

    return np.transpose(c), r


def emd(t, y, Nmodes=None):
    """
    参数
    ----------
    t : 1D 数组
        独立数据, 长度 N.
    y : 1D 数组
        独立数据 长度 N.
    Nmodes : int, 可选
        最大返回模式数量

    Returns
    -------
    c : 2D 数组
        一个 NxM 数组可以给出M个经验模式作为列
    r : 1D 数组
        残差项, 长度 N.

    ----------
    """

    t, y = map(np.asarray, [t, y])
    if t.ndim > 1:
        raise ValueError("t array must be 1D")
    if y.ndim > 1:
        raise ValueError("y array must be 1D")

    c = np.empty([len(y), 0])
    h, r = map(np.copy, [y, y])
    hold = np.zeros(y.shape)
    while True:
        try:
            while True:
                h = sift(t, h)
                var = np.sum((h-hold)**2 / hold**2)
                if var < 0.25:
                    c = np.append(c, h[:, np.newaxis], axis=1)
                    r = r - h
                    if len(c) == Nmodes:                  #如果不想要更多的模式
                        return c, r

                    h = r
                    hold = np.zeros(y.shape)
                    break
                hold = h
        except FlatFunction:                  #如果残差极值太少
            return c, r


class FlatFunction(Exception):
    pass


def sift(t, y, nref=100, plot=False):
    """
    通过将样条包络线拟合到极值，识别出一系列数据中占主导地位的“外在模式”。

    参数
    ----------
    t : 1D 数组
        独立数据, 长度 N.
    y : 1D 数组
        独立数据, 长度 N.
    nref : int, 可选
        拟合样条时，要反映每个端点的extema个数。
    plot : {True|False}, 可选
        如果 True, 使用matplotlib创建函数和结果的诊断图。pyplot情节功能。如果有一个活动的alread plot窗口，那么绘图将在那里完成。不会返回绘图句柄。
    Returns
    -------
    h : 1D 数组
        即主要模式, 长度 N.

    """


    argext = _allrelextrema(y)                           #确定相对极值

    if len(argext) < 2:                                  #如果极值太少则抛出异常
        raise FlatFunction('这个序列中的max和min太少了，无法筛选')

    inclleft = not _inrange(y[[0]], y[argext[0]], y[argext[1]])   #如果左端点和右端点超出了最近的两个极值设置的限制，则将它们作为极值
    inclright = not _inrange(y[[-1]], y[argext[-2]], y[argext[-1]])
    if inclleft and inclright: argext = np.concatenate([[0], argext, [-1]])
    if inclleft and not inclright: argext = np.insert(argext, 0, 0)
    if not inclleft and inclright: argext = np.append(argext, -1)

    T, E  = t[argext], y[argext]                                  #现在把两边的极值都反映出来
    tleft, yleft = T[0] - (T[nref:0:-1] - T[0]) , E[nref:0:-1]
    tright, yright = T[-1] + (T[-1] - T[-2:-nref-2:-1]), E[-2:-nref-2:-1]
    tall = np.concatenate([tleft, T, tright])
    yall = np.concatenate([yleft, E, yright])

    if yall[0] < yall[1]:                                         #解析出最小值和最大值。极值必须是交替的，所以只要找出是最小值还是最大值先出现
        tmin, tmax, ymin, ymax = tall[::2], tall[1::2], yall[::2], yall[1::2]
    else:
        tmin, tmax, ymin, ymax = tall[1::2], tall[::2], yall[1::2], yall[::2]

    if len(tmin) < 4 or len(tmax) < 4:                                   #再次检查是否有足够的极值，现在可能已经添加了端点
        raise FlatFunction('这个序列中的max和min太少了，无法筛选')

    spline_min, spline_max = map(interp1d, [tmin,tmax], [ymin,ymax], ['cubic']*2)   #计算样条enevlopes和均值
    m = (spline_min(t) + spline_max(t))/2.0
    h = y - m

    if plot:
        plt.plot(t, y, '-', t, m, '-')
        plt.plot(tmin, ymin, 'g.', tmax, ymax, 'k.')
        tmin = np.linspace(tmin[0], tmin[-1], 1000)
        tmax = np.linspace(tmax[0], tmax[-1], 1000)
        plt.plot(tmin, spline_min(tmin), '-r', tmax, spline_max(tmax), 'r-')

    return h


def _allrelextrema(y, tol=0.0):
    """
    在使用sci .signal的一半时间内按顺序找到所有相对极值。
    函数并结合argrel{min|max}的结果。scipy。信号版本也错过多点最大和分钟。
    这个版本返回多点极值的中点，或者多点exrtema的中点。
    """

    slope = np.diff(y)        #计算连续值之间的差值(如斜率)
    slope[np.abs(slope) < tol] = 0.0

    nonzero = (slope != 0.0)    #跟踪原始索引时删除所有零
    slope = slope[nonzero]
    indices = np.arange(len(y) - 1)
    indices = indices[nonzero]

    slope_sign = np.zeros(len(slope), 'i1')    #我们只要求斜率的符号
    slope_sign[slope > 0] = 1
    slope_sign[slope < 0] = -1

    curve_sign = np.diff(slope_sign)      #这样我们就能求出两边斜率符号不同的点的曲率符号
    arg_curve_chng = np.nonzero(curve_sign != 0)[0]
    i0 = indices[arg_curve_chng]
    i1 = indices[arg_curve_chng + 1] + 1
    i = np.floor((i0 + i1) / 2.0)

    return i.astype(int)


def _inrange(y, y0, y1):
    """
    如果y在range (y0, y1)，返回True
    """
    if y0 > y1:
        return (y < y0) and (y > y1)
    else:
        return (y > y0) and (y < y1)


def _reflect(x0, x):
    return x0 - (x - x0)


def _oppsign(x, y, tol):
    return (x < -tol and y > tol) or (x > tol and y < -tol)
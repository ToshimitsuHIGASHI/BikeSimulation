# -*- coding: utf-8 -*-
import sys
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
# from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d.art3d as art3d
# import matplotlib.animation as animation
import numpy as np
import datetime
from matplotlib.transforms import CompositeGenericTransform
from matplotlib.transforms import Affine2D

# ##################################################################
# 入力パラメータの設定
# ##################################################################

# 回転角の入力
DELTAOMEGA = 0.1

# 車輪データの要素数（＝エレメント数）の定義
ELEMENTS = 1000

# 描画関係パラメータ
NFR = 900  # Number of frames 動画の再現枚数（1回のシミュレーションで描画する枚数）
FPS = 500  # Frame per sec

# キャスター角 := THETA
THETA = 70
THETA_RAD = THETA * np.pi / 180

# 車輪回転角の限界値（実際にハンドルが曲がる限界）
STEERING_LIMIT = 50

# トレール長の設定．フロントフォーク（＝ハンドル回転中心）と前輪中心間の距離となる．
OFFSET = 10

# 車輪径の定義
DIAMETER = 20

# ホイルベースの定義
WHEEL_BASE = 100

# 回転中心の定義
# 回転中心は前輪と後輪の接地点で結ばれたベクトルとなる
POINT_1 = np.array([0, 0, DIAMETER - OFFSET / math.cos(THETA_RAD)])
POINT_2 = np.array([DIAMETER/math.tan(THETA_RAD) - OFFSET/math.sin(THETA_RAD),
                    0, 0])
ROTATE_CENTER = POINT_2 - POINT_1
print("Point1 = ", POINT_1)
print("Point2 = ", POINT_2)

# 前輪中心の設定
WHEEL_O = np.array([np.zeros(ELEMENTS),
                    np.zeros(ELEMENTS),
                    DIAMETER*np.ones(ELEMENTS)])

# 微小区間εの定義
EPSILON = sys.float_info.epsilon
# print('epsilon = ', EPSILON)

# ##################################################################
# 回転元の点の指定
# ##################################################################
# 未使用のためコメントアウト
# O = np.array([0, 0, 0])             # 原点位置

# 回転前の座標を設定
B = np.array([-2, -2, 1])


# ##################################################################
# サブ関数の定義
# ##################################################################
def calcRotCentVector(param1, param2):
    """回転中心ベクトル算出関数
    """

    # 回転中心ベクトルの算出
    n = param1 - param2
    print("n = ", n)

    # 回転中心ベクトルのノルムを導出
    norm_n = np.linalg.norm(n)

    # 回転中心基本ベクトルの算出
    input_n = n / norm_n

    # 回転中心基底ベクトルの出力
    return input_n


def plotDot(ax, pr_bb, pr_color):
    """点の描画処理（点，色）指定
    """

    for x, y, z in [pr_bb]:
        ax.scatter(x, y, z, color=pr_color, marker='s')


def arrow(ax, v, sp, c):
    """矢印の描画

    関数名(始点位置，ベクトル，色)
    始点位置を基準としてでベクトルで示した方向にプロットする
    v:始点位置、sp:ベクトル、c:色
    """
    # ax.quiver(v[0]+sp[0], v[1]+sp[1], v[2]+sp[2],
    #          v[0], v[1], v[2],
    #          length=np.linalg.norm(v),
    #          color=c, linewidth=3)
    ax.quiver(v[0], v[1], v[2],
              sp[0], sp[1], sp[2],
              # length=np.linalg.norm(sp),
              np.linalg.norm(sp),
              color=c, linewidth=3)
    # print("ベクトル sp の大きさ", np.linalg.norm(sp))


'''未使用のためコメントアウト
def plotWheel(Ax, data):
    """車輪の描画
    """
    for angle in range(0, 360):
        # 現在描写されているグラフを消去．
        # 使用してもアニメーション描画できなかったので削除した
        # plt.cla()
        wheelData = DotDot_Itr[angle]
        for x, y, z in wheelData:
            ax.scatter(x, y, z, color='r', marker='s')
'''


def rtnArb_Rot(promega, n):
    """右手座標系の回転処理関数（回転角，回転中心ベクトル）

    回転角はdegree（0〜360°）を入力する．
    """
    n_x = n[0]
    n_y = n[1]
    n_z = n[2]
    t = promega*np.pi/180
    rot_rod = np.array([[np.cos(t) + n_x**2*(1-np.cos(t)),
                         n_x*n_y*(1-np.cos(t)) - n_z*np.sin(t),
                         n_x*n_z*(1-np.cos(t)) + n_y*np.sin(t)],
                        [n_y*n_x*(1-np.cos(t)) + n_z*np.sin(t),
                         np.cos(t) + n_y**2*(1-np.cos(t)),
                         n_y*n_z*(1-np.cos(t)) - n_x*np.sin(t)],
                        [n_z*n_x*(1-np.cos(t)) - n_y*np.sin(t),
                         n_z*n_y*(1-np.cos(t)) + n_x*np.sin(t),
                         np.cos(t) + n_z**2*(1-np.cos(t))]])
    # print("Rot_Rod = ", rot_rod)
    return rot_rod


def rotM(p):
    """ 回転行列算出関数

    例
    p = np.array([np.pi, np.pi/2, np.pi/3])
    R = rotM(p)
    A = R.T
    """
    # 回転行列を計算する
    px = p[0]
    py = p[1]
    pz = p[2]

    # 物体座標系の 1->2->3 軸で回転させる
    rx = np.array([[1, 0, 0],
                   [0, np.cos(px), np.sin(px)],
                   [0, -np.sin(px), np.cos(px)]])
    ry = np.array([[np.cos(py), 0, -np.sin(py)],
                   [0, 1, 0],
                   [np.sin(py), 0, np.cos(py)]])
    rz = np.array([[np.cos(pz), np.sin(pz), 0],
                   [-np.sin(pz), np.cos(pz), 0],
                   [0, 0, 1]])
    r = rz.dot(ry).dot(rx)

    return r


# ##################################################################
# クラス定義
# ##################################################################
class Wheel2D:
    """2Dグラフ用のデータクラス
    """
    # 接地点の初期化
    # 前輪描画データ：PtGnd_F
    # 後輪描画データ：PtGnd_R
    # PtGnd_F = np.empty((0, 3), int)
    # PtGnd_R = np.empty((0, 3), int)

    # 描画データの初期化（前輪）車輪の360°回転分のデータ（x，y，z軸）要素数＝3600個
    xfG = []
    yfG = []
    zfG = []

    # キャンバー角でのセルフステアによる軌跡
    xfGC = []
    yfGC = []
    zfGC = []
    xfGD = []
    yfGD = []
    zfGD = []

class Bike:
    """オートバイのデータクラス
    """
    # キャスター角 := THETA
    def __init__(self):
        self.theta = THETA
        self.theta_rad = THETA_RAD
        # トレール長の設定．フロントフォーク（＝ハンドル回転中心）と前輪中心間の距離となる．
        self.offset = OFFSET
        # 車輪径の定義
        self.diameter = DIAMETER
        # 回転中心
        self.rotate_center = ROTATE_CENTER
        # 前輪中心の設定
        self.wheel_o = WHEEL_O
        # 回転後の前輪中心
        self.f_center = np.array([0, 0, DIAMETER])
        # 後輪中心（後輪の中心は変わらない）
        self.r_center = np.array([-WHEEL_BASE, 0, DIAMETER])
        # 前輪データ（途中産出値）
        self.wd = Wheel2D()
        # 前輪データ（初期値）
        self.wheel_init = np.empty((0, 3), int)
        # バンク後の車輪データ（バンク中の暫定車輪データ）の定義
        self.wheel_move = np.empty((0, 3), int)

# ##################################################################
# 設定値の内部パラメータへの変換
# ##################################################################
"""未使用のためコメントアウト
# print('n = ', n)
norm_n = np.linalg.norm(ROTATE_CENTER)
# print('norm of n = ', norm_n)
input_n = ROTATE_CENTER / norm_n
# print("input_n = ", input_n)

# 設定した回転角と回転中心に応じた回転行列を導出
R = rtnArb_Rot(DELTAOMEGA, input_n)
"""

# ##################################################################
# 初期位置の車輪を設定，描画
# 1回目の回転後の前輪点群データを算出
# ##################################################################
def calc_front_wheel():

    # バイククラスの初期化
    bike = Bike()

    # 回転角の定義
    omega = np.linspace(0, 2*np.pi, ELEMENTS)
    # print("type of omega = ", type(omega))
    # print("shape of omega = ", np.shape(omega))
    # print("omega = ", omega)
    bike.wheel_init = [DIAMETER * np.cos(omega),
                       np.zeros(ELEMENTS),
                       DIAMETER * np.sin(omega)] + WHEEL_O

    # ##################################################################
    # 回転処理
    # ##################################################################

    # 回転中心ベクトルの設定
    input_n = calcRotCentVector(POINT_1, POINT_2)
    print("input_n", input_n)

    # ハンドル回転処理：　フロントフォークを中心に車輪を回転させる．
    # 0°から359°まで前輪，後輪を倒した時のそれぞれのデータ（前輪，後輪）の算出及び描画処理を
    # 実行する
    # 前輪データ： PtGnd_F
    # 後輪データ： PtGnd_R
    # leanAngle: 傾き角（リーン角）→0°〜360°まで傾ける
    # range：　反復回数を示す．1回当たりの変化量が0.1なので，反復回数＝3600で傾き角＝360°
    #         となる．

    # 1回の遷移は0.1°．ハンドルを360°回転させる．range()の引数に指定できるのは整数intのみ
    for omega in range(0, 3600):

        # 設定した回転角と回転中心に応じた回転行列を導出
        r = rtnArb_Rot(0.1, input_n)

        # iCounter = 0

        # 回転後の前輪データの算出
        # ハンドル回転角度＝0°の初期車輪位置：　wheel_init
        # wheel_initを回転行列rを経てomega分だけ回転させた時の車輪はwheel_moveになる．
        # print("WheelInit = ", wheel_init)
        bike.wheel_move = np.dot(r, bike.wheel_init)
        row, col = bike.wheel_move.shape
        
        # 前輪と後輪共通の接平面を算出
        dd_tan_tmp = calc_tangent(bike.wd)

        # 接地点データの抽出
        # 接平面に接する前輪データを抽出
        min_index = np.argmin(bike.wheel_move[2, :])
        # print("min_index = ", min_index)
        # print("minimum of wheel_move = ", np.min(wheel_move[2,:]))

        # 接地点データをX軸，Y軸，Z軸の値に分解，保存
        bike.wd.xfG.append(bike.wheel_move[0, min_index])
        bike.wd.yfG.append(bike.wheel_move[1, min_index])
        bike.wd.zfG.append(bike.wheel_move[2, min_index])

        # 接地点データからハンドル旋回角分のデータを抽出
        if omega <= STEERING_LIMIT*10:
            bike.wd.xfGC.append(bike.wheel_move[0, min_index])
            bike.wd.yfGC.append(bike.wheel_move[1, min_index])
            bike.wd.zfGC.append(bike.wheel_move[2, min_index])
        elif 3600 - STEERING_LIMIT*10 <= omega <= 3600:
            bike.wd.xfGD.append(bike.wheel_move[0, min_index])
            bike.wd.yfGD.append(bike.wheel_move[1, min_index])
            bike.wd.zfGD.append(bike.wheel_move[2, min_index])
        
        bike.wheel_init = bike.wheel_move

    return bike


# ##################################################################
# 接平面の算出
# ##################################################################
def calc_tangent(wd):
    """接平面の算出
    関数名(前輪の点群データ：3次元配列)
    右手座標系の回転処理語の前輪点群データと後輪の点群データ（固定）
    の接平面(Ground：3次元ベクトル)を算出する．
    但し接平面のX軸ベクトルは0となる．Y軸とZ軸の値だけとなる．
    WD: calc_front_wheel()の算出結果
    """
    rtn_wd = wd
    return rtn_wd


# ##################################################################
# 2次元グラフの表示処理
# ##################################################################
def draw_2d_graph(wd):
    '''2次元グラフ表示処理
    '''
    ffig = plt.figure(figsize=(DIAMETER/0.9, DIAMETER/1.6), dpi=80)
    dAx = ffig.add_subplot(111)
    dAx.set_title("Trajectory of Turning Handle at 360 degrees")
    dAx.set_xlim(-(2*DIAMETER+2), 2*np.pi*10)
    dAx.set_ylim(-(2*DIAMETER+2), 2*DIAMETER+1)
    dAx.spines['right'].set_color('none')
    dAx.spines['top'].set_color('none')
    dAx.xaxis.set_ticks_position('bottom')
    dAx.spines['bottom'].set_position(('data', 0))
    # plt.xticks([-40, -20, 0, 10*np.pi/2, 20*np.pi],
    #            [r'$40$', r'$20$', r'$0$', r'$+\np.pi/2$', r'$+2\np.pi$'])
    dAx.yaxis.set_ticks_position('left')
    dAx.spines['left'].set_position(('data', 0))
    dAx.set_xlabel("Turning Direction", horizontalalignment='right', x=1.0)
    dAx.set_ylabel("Traveling  Direction", horizontalalignment='right', y=1.0)
    # グラフのグリッドを正方形にする
    dAx.set_aspect('equal')

    # 90度回転
    t = CompositeGenericTransform(Affine2D.identity().rotate_deg(90),
                                  dAx.transData)
    # 回転しない（0°回転）
    # t = CompositeGenericTransform(Affine2D.identity().rotate_deg(0),
    #                               dAx.transData)
    dAx.plot(wd.xfG, wd.yfG, color="red", linestyle="-", transform=t)
    dAx.plot(wd.xfGC, wd.yfGC, color="red", linestyle="solid", linewidth=3,
             transform=t)
    dAx.plot(wd.xfGD, wd.yfGD, color="red", linestyle="solid", linewidth=3,
             transform=t)

    dAx.text(DIAMETER, DIAMETER,
             r'Chaster angle = {0} degree,  Diameter = {1} '
             .format(THETA, DIAMETER))
    dAx.text(DIAMETER, DIAMETER - 2,
             r'Offset between center of the wheel and caster = {0} '
             .format(OFFSET))
    dAx.text(DIAMETER, DIAMETER - 4,
             r'Steering angle is {0} degree.'
             .format(STEERING_LIMIT))
    dAx.text(DIAMETER, DIAMETER - 6,
             r'Thick red line shows a trajectory which touches a ground '
             'from -{0} degree to {1} degree in steering angle'
             .format(STEERING_LIMIT, STEERING_LIMIT), color='red')

    d = datetime.datetime.today()
    ffig.savefig("Trail_"+d.strftime("%B%d日%A")+"Caster="+str(THETA)
                 + "_Wheel＝"+str(DIAMETER)+"_Offset="+str(OFFSET)+".png",
                 dpi=100, transparent=False)


def draw_3d_graph(wd):
    """3次元プロット表示処理
    """
    # プロット
    fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    ax = fig.gca(projection='3d')
    ax.set_aspect('auto')
    sct, = ax.plot([], [], [], "o", markersize=3)

    # 描画を最大化し，グラフ範囲を正方形にしたい時はset_aspect('equal', 'datalim')
    # にすると良い．
    # ax.set_aspect('equal', 'datalim')

    # タイヤのサイズを小さくして形状をリアル（真円）にしたい場合は下記のコードを憂苦に
    # すると良い．
    ax.tick_params(axis='x', length=40.0)
    ax.tick_params(axis='y', length=40.0)
    ax.tick_params(axis='z', length=20.0)
    ax.set_xlim(-2 * DIAMETER, 2 * DIAMETER)
    ax.set_ylim(-2 * DIAMETER, 2 * DIAMETER)
    ax.set_zlim(0, 4 * DIAMETER)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.set_aspect('auto')

    # ##################################################################
    # 描画データの定義，描画処理
    # ##################################################################
    # 未使用のためコメントアウト
    # im = []  # フレーム更新の際に前回のプロットを削除するために用意
    # imgif = [] # フレーム更新の際に前回のプロットを削除するために用意．gifアニメ用

    # ##################################################################
    # 回転軸の表示
    # ##################################################################
    # arrow(ax, POINT_1, POINT_2, 'k')
    # line= art3d.Line3D(POINT_1[0], POINT_1[1], POINT_1[2],
    #                    POINT_2[0], POINT_2[1], POINT_2[2], color="k")
    point_3 = [-1*(POINT_1[0]+DIAMETER * 1.2),
               POINT_1[1],
               POINT_1[2]+math.tan(THETA_RAD)*DIAMETER*1.2]
    ax.plot([POINT_1[0], point_3[0]],
            [POINT_1[1], point_3[1]],
            [POINT_1[2], point_3[2]], color="k")
    # ax.add_line(line)

    # ##################################################################
    # 車輪の表示
    # ##################################################################
    # 車輪中心
    ax.plot([0], [0], [DIAMETER], marker="o", linestyle='None')
    # 車輪
    # Draw a circle on the y=0
    q = Circle((0, DIAMETER), DIAMETER, color='red', fill=False)
    ax.add_patch(q)
    art3d.pathpatch_2d_to_3d(q, z=0, zdir="y")

    # ##################################################################
    # 接地点の表示
    # ##################################################################
    # 車輪データのテスト描画
    # 周回後の最終位置にある車輪を描画する．
    # 色は自動的に指定される．
    ax.scatter(wd.xfG, wd.yfG, wd.zfG, s=40, alpha=0.3, marker=".")

    def update(ifrm, xa, ya, za, xb, yb, zb):
        """描画データ属性の設定
        """
        sct.set_data(xa[ifrm], ya[ifrm])
        sct.set_3d_properties(za[ifrm])
        sct.set_data(xb[ifrm], yb[ifrm])
        sct.set_3d_properties(zb[ifrm])

    def _update_plot(i, fig, im, xa, ya, za):
        """更新する内容
        """
        # 前回のフレーム内容を一旦削除
        if len(im) > 0:
            im[0].remove()
            im.pop()

        # print('i = ', i)
        # print('xa[i] = ', xa[i])
        # 複数の点を描画する際は，x，y，zを配列表記にしてscatter関数の引数にする．
        # im.append(ax.scatter([xa[i], xb[i]],
        #                      [ya[i], yb[i]],
        #                      [za[i], zb[i]],
        #                      s=20, alpha=0.3, color='c', marker='o'))
        im.append(ax.scatter(xa[i], ya[i], za[i],
                             s=20, alpha=0.3, color='c', marker='o'))
        print('*')
        # im.append(ax.scatter(xa[i], ya[i], za[i],
        #                      s=20, alpha=0.3, color='c', marker='o'))


# ##################################################################
# 描画データファイルの保存，描画処理
# ##################################################################

# アニメーション作成
# アニメーション機能は削除する
'''
ani = animation.FuncAnimation(fig, _update_plot, frames=NFR,
                              fargs=(fig, im, xfG, yfG, zfG),
                              interval=1000/FPS)
# aniFront = animation.FuncAnimation(fig, _update_plot, NFR,
#                                    fargs=(fig, im, xfG, yfG, zfG,
#                                           xrG, yrG, zrG),
#                                    interval=1000/FPS)
# aniRear  = animation.FuncAnimation(fig, _update_plot, NFR,
#                                    fargs=(fig, im, xrG, yrG, zrG),
#                                    interval=1000/FPS)

d = datetime.datetime.today()
FFig.savefig("Trail"+d.strftime("%B%d日%A")+"Caster="+str(THETA)
             + "_Wheel＝"+str(DIAMETER)+"_Offset="+str(OFFSET)+".png",
             dpi=100,transparent = False)
plt.show()
'''
'''　アニメーション機能は削除する
directory = '/Users/east/programming/Python/BicycleModeling/MovieGIF/'
fn = 'plot_BicycleTrajectory'+ str(datetime.datetime.now())

# ani.save(directory+fn+'.gif', writer='imagemagick')
ani.save(directory+fn+'.mp4', writer='ffmpeg', fps=FPS)
'''

if __name__ == '__main__':
    bike = calc_front_wheel()
    print(type(bike.wd))
    print("bike.wheel_o = ", bike.wheel_o)
    print("f_center = ", bike.f_center)
    print("r_center = ", bike.r_center)
    draw_2d_graph(bike.wd)
    draw_3d_graph(bike.wd)
    plt.show()

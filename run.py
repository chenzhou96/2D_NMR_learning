import operator_operation as oo

# 参数设置
## 路径
PATH = '/Users/zhouchen/Documents/CS_project/2D_NMR_learning/operator_operation_table.csv'
## 定义可检测的宏观磁化矢量
WELL_BEHAVED_VECTORS = {'Ix', 'Iy', 'Sx', 'Sy'}
## 定义起始宏观磁化矢量 一般为 Iz
MM_VECTORS = [oo.Vector('Iz'),]
# MM_VECTORS = [Vector('Iy', False, 'cos(πJt1)'),]
## 脉冲算符 θIx, θIy: θ为脉冲角度 Ix/Iy为单位算符
## 在xy平面的转动算符 2πδIt1Iz: δI为I原子核的化学位移 t1为旋转时间
## 两核的耦合作用算符 πJt2: J为两核的耦合常数 t2为耦合作用时间
OPERATORS = [
    oo.Vector('Ix', coefficient='90'),
    oo.Vector('Sx', coefficient='90'),
    oo.Vector('Iz', coefficient='2πδIt1'),
    oo.Vector('Sz', coefficient='2πδst1'),
    oo.Vector('IzSz', coefficient='πJt1'),
    oo.Vector('Ix', coefficient='180'),
    oo.Vector('Sx', coefficient='180'),
    oo.Vector('Iz', coefficient='2πδIt2'),
    oo.Vector('Sz', coefficient='2πδst2'),
    oo.Vector('IzSz', coefficient='πJt2'),
    # Vector('Iz', coefficient='2πδIt2'),
    # Vector('Sz', coefficient='2πδIt2'),
    # Vector('IzSz', coefficient='πJt2'),
]
# 设置结束

if __name__ == '__main__':

    table = oo.read_table(PATH)
    for operator in OPERATORS:
        if operator.vector not in oo.well_behaved_vector(table):
            print('\n输入非法算符, 请检查\n')
            exit()

    results = oo.vector_calculate(MM_VECTORS, OPERATORS, table)
    detected_vectors = list()
    for result in results:
        # if result.vector in WELL_BEHAVED_VECTORS:
        if True:
            # result = _simplify_result(result)
            if result.symbol:
                detected_vectors.append(f'+{result.coefficient}{result.vector}')
            else:
                detected_vectors.append(f'-{result.coefficient}{result.vector}')

    if detected_vectors:
        print('\n可检测磁化矢量:')
        for detected_vector in detected_vectors:
            print(detected_vector)
        print('')
    else:
        print('\n无可检测磁化矢量\n')
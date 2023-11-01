from copy import deepcopy
import pandas as pd

class Coefficient():
    """
    系数类 包含三角函数类型和自变量
    三角函数为bool类型 0代表cos 1代表sin
    参数: trig, argu, index
    """

    def __init__(self, trig: bool, argu: str, index = 1) -> None:
        self.trig = trig
        self.argu = argu
        self.index = index

    def __eq__(self, __value: object) -> bool: # 用于判断该类是否在列表中
        return self.trig == __value.trig and self.argu == __value.argu and self.index == __value.index

class Vector():
    """
    向量类 包含数值,符号,和系数
    符号为bool类型 0代表负 1代表正
    参数: vector, symbol, coefficient, coefficient_list
    """

    def __init__(self, vector: str, symbol=True, coefficient = '', mul = 1) -> None:
        self.vector = vector # Iy
        self.symbol = symbol
        self.coefficient = coefficient # 所有三角函数形式的系数
        self.coefficient_list = list()
        self.exsit = True
        self.mul = mul # 待补充

    # 已补充 增加相同Coefficient.trig, Coefficient.argu情况下Coefficient.index的合并
    def str_to_list(self):
        """
        将Vector.coefficient转换为Vector.coefficient_list
        """

        # 保证Vector.coefficient和Vector.coefficient_list必有一个为空
        if self.coefficient_list:
            print('\n数据报错\nfrom str_to_list\n')
            exit()

        coefficients = self.coefficient.split(',')

        trig_dict = dict() # 中间字典 存储Coefficient类的三角函数
        for coefficient in coefficients: # coefficients是由字符串组成的列表
            if coefficient:
                if coefficient[3] == '(': # 说明sin或cos不带幂指数
                    key = coefficient
                    value = 1
                else:
                    key = f'{coefficient[:3]}{coefficient[4:]}'
                    value = int(coefficient[3])
                
                if key in trig_dict:
                    trig_dict[key] += value
                else:
                    trig_dict[key] = value
        # 此时 trig_dict存储者Coefficient类所需的三个参数

        trig_list = list()
        for key, value in trig_dict.items():
            trig_str, argu = key.split('(') # 注意argu末尾还带着右括号
            trig = trig_str[0] == 's' # 如果是sin则为真 反之为假
            class_trig = Coefficient(trig, argu[:len(argu)-1], value)

            if class_trig.argu == '90' and class_trig.trig == True:
                continue
            if class_trig.argu == '180' and class_trig.trig == False:
                if value % 2 != 0:
                    self.symbol = not self.symbol
                continue

            trig_list.append(class_trig)
        
        self.coefficient_list = trig_list
        self.coefficient = ''

        return self
    
    def list_to_str(self):
        """
        将Vector.coefficient_list转换为Vector.coefficient
        """

        # 保证Vector.coefficient和Vector.coefficient_list必有一个为空
        if self.coefficient:
            print('\n数据报错\nfrom list_to_str\n')
            exit()

        cos_sin = ['cos', 'sin']
        coefficients = list() # 中间列表 存储字符串格式的每个三角函数
        for trig_fun in self.coefficient_list:
            if trig_fun.index:
                if trig_fun.index == 1:
                    trig_str = f'{cos_sin[int(trig_fun.trig)]}({trig_fun.argu})'
                else:
                    trig_str = f'{cos_sin[int(trig_fun.trig)]}{trig_fun.index}({trig_fun.argu})'
                coefficients.append(trig_str)
        
        self.coefficient = ','.join(coefficients)
        self.coefficient_list = list()

        return self

def read_table(path: str) -> pd.DataFrame:
    """
    读入算符运算表 保存在DataFrame格式表格中
    """

    data = pd.read_csv(path)

    return data.set_index('vector')

def well_behaved_vector(table: pd.DataFrame) -> set:
    """
    根据算符表 输出合格向量
    """

    return set(table.index) | set(table.columns)

def operator_calculate(mm_vector: Vector, operator: Vector, table: pd.DataFrame) -> list:
    """
    输入起始向量,变换算符,和算符运算表 返回计算后的算符列表
    """

    result = table[operator.vector][mm_vector.vector]

    if result == 'E':
        return [mm_vector,]
    
    mm_vector_1 = Vector(mm_vector.vector, mm_vector.symbol, f'{mm_vector.coefficient},cos({operator.coefficient})')
    if result[-1] == '-':
        mm_vector_2 = Vector(result[:-1], not mm_vector.symbol, f'{mm_vector.coefficient},sin({operator.coefficient})')
    else:
        mm_vector_2 = Vector(result, mm_vector.symbol, f'{mm_vector.coefficient},sin({operator.coefficient})')
    
    if operator.coefficient == '90':
        return [mm_vector_2,]
    elif operator.coefficient == '180':
        return [mm_vector_1,]
    return [mm_vector_1, mm_vector_2]

def vector_calculate(mm_vectors: list, operators: list, table: pd.DataFrame) -> list:
    """
    输入变换前宏观磁化矢量组,变换算符,和算符运算表 返回变换后宏观磁化矢量组
    """

    for operator in operators:

        new_mm_vectors = list()
        for mm_vector in mm_vectors:
            new_mm_vectors.extend(operator_calculate(mm_vector, operator, table))

        mm_vectors = simplify_results(new_mm_vectors)
    
    return mm_vectors

# 待补充磁化矢量之间的互相简化
# 1. sin2(x) + cos2(x) = 1 已完成
# 2. -sin(x) + sin(x) = 0 已完成
# 3. cos2(x) - sin2(x) = cos(2x) 已完成
# 4. cos(x)sin(x) + sin(x)cos(x) = sin(2x)
def simplify_results(mm_vectors: list) -> list:
    """
    输入宏观磁化矢量组 返回简化后的结果
    """

    for mm_vector in mm_vectors:
        mm_vector.str_to_list()
    
    flag = True # 标记是否化简到最简形式
    while flag:
        flag = False
        new_vectors = list() # 临时存储产生的新矢量
        num = len(mm_vectors)
        # 简化 公式1 & 3
        for index1 in range(num):
            mm_vector1 = mm_vectors[index1]
            if mm_vector1.exsit:
                for index2 in range(index1 + 1, num):
                    mm_vector2 = mm_vectors[index2]
                    if mm_vector2.exsit and mm_vector1.vector == mm_vector2.vector:
                        # 寻找可能满足公式1的矢量
                        diff = list()
                        for trig1 in mm_vector1.coefficient_list:
                            if trig1 not in mm_vector2.coefficient_list:
                                diff.append(trig1)
                                if len(diff) > 1:
                                    break
                        if len(diff) == 1:
                            trig1= diff[0]
                            for trig2 in mm_vector2.coefficient_list:
                                if trig2 not in mm_vector1.coefficient_list:
                                    break
                            # 找到值得化简的一对矢量 差异系数在于trig1和trig2 已验证
                            if trig1.argu == trig2.argu and trig1.index > 1 and trig2.index > 1 and trig1.trig != trig2.trig:
                                trig1.index -= 2
                                trig2.index -= 2
                                if mm_vector1.symbol == mm_vector2.symbol: # 公式1
                                    if not trig1.index:
                                        mm_vector1.coefficient_list.remove(trig1)
                                    if not trig2.index:
                                        mm_vector2.coefficient_list.remove(trig2)
                                    if not trig1.index and not trig2.index:
                                        mm_vectors[index2].exsit = False
                                else: # 公式3
                                    new_coefficient = deepcopy(mm_vector1.coefficient_list)
                                    new_coefficient.remove(trig1)
                                    new_coefficient.append(Coefficient(False, f'2{trig1.argu}'))
                                    if not trig1.trig:
                                        new_vector = deepcopy(mm_vector1)
                                    else:
                                        new_vector = deepcopy(mm_vector2)
                                    new_vector.coefficient_list = new_coefficient
                                    new_vectors.append(new_vector)
                                    if not trig1.index:
                                        mm_vectors[index1].exsit = False
                                    if not trig2.index:
                                        mm_vectors[index2].exsit = False

        if new_vectors:
            mm_vectors.extend(new_vectors)
        
        # 简化 公式2
        for index1 in range(num):
            mm_vector1 = mm_vectors[index1]
            if mm_vector1.exsit:
                for index2 in range(index1 + 1, num):
                    mm_vector2 = mm_vectors[index2]
                    if mm_vector2.exsit and mm_vector1.vector == mm_vector2.vector and mm_vector1.symbol != mm_vector2.symbol:
                        # 寻找可能满足公式2的矢量
                        same_or_not = True
                        for trig in mm_vector1.coefficient_list:
                            if trig not in mm_vector2.coefficient_list:
                                same_or_not = False
                                break
                        if same_or_not:
                            mm_vectors[index1].exsit = False
                            mm_vectors[index2].exsit = False
        
        for mm_vector in mm_vectors[:]:
            if not mm_vector.exsit:
                mm_vectors.remove(mm_vector)
                flag = True

    for mm_vector in mm_vectors:
        mm_vector.list_to_str()

    return mm_vectors

if __name__ == '__main__':

    pass
    test = Vector('Iy', True, ',sin(90),cos2(2πδIt1),cos(πJt1),cos(180),cos(2πδIt2),cos(πJt2),cos(πJt1)')
    # test.str_to_list().list_to_str()
    test1 = Vector('Iy', True, ',sin(90),sin2(2πδIt1),cos(πJt1),cos(180),cos(2πδIt2),cos(πJt2),cos(πJt1)')
    # test1.str_to_list().list_to_str()
    test2 = Vector('Iy', True, ',sin(90),cos(πJt1),cos(2πδIt2),cos(πJt2),cos(πJt1)')
    test3 = Vector('Iy', True, ',sin(90),sin2(2πδIt1),cos(πJt1),cos(180),cos(2πδIt2),cos(πJt2),cos(πJt1)')
    mm_vectors = simplify_results([test, test1, test2, test3])
    for mm_vector in mm_vectors:
        if mm_vector.exsit:
            print(mm_vector.coefficient)
    # print(test.symbol, test.coefficient)
    # output: sin2(2πδIt1),cos2(πJt1),cos(2πδIt2),cos(πJt2)
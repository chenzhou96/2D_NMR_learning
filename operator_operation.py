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

class Vector():
    """
    向量类 包含数值,符号,和系数
    符号为bool类型 0代表负 1代表正
    参数: vector, symbol, coefficient, coefficient_list
    """

    def __init__(self, vector: str, symbol=True, coefficient = '', coefficient_list = list()) -> None:
        self.vector = vector
        self.symbol = symbol
        self.coefficient = coefficient
        self.coefficient_list = coefficient_list

    # 已补充 增加相同Coefficient.trig, Coefficient.argu情况下Coefficient.index的合并
    def str_to_list(self):
        """
        将Vector.coefficient转换为Vector.coefficient_list
        """

        # 保证Vector.coefficient和Vector.coefficient_list必有一个为空
        if self.coefficient_list:
            print('\n数据报错\n')
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
                    trig_dict[key] = 1
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
            print('\n数据报错\n')
            exit()

        cos_sin = ['cos', 'sin']
        coefficients = list() # 中间列表 存储字符串格式的每个三角函数
        for trig_fun in self.coefficient_list:
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

        mm_vectors = new_mm_vectors
    
    return mm_vectors

# 待补充磁化矢量之间的互相简化
# 1. sin2(x) + cos2(x) = 1
# 2. 
def simplify_results(mm_vectors: list) -> list:
    """
    输入宏观磁化矢量组 返回简化后的结果
    """

    # 先简化各个单独的宏观磁化矢量 找出幂次大于等于2的项
    new_vectors = list()
    for mm_vector in mm_vectors:
        mm_vector = Vector('') # 写代码用 写完注释掉
        mm_vector.str_to_list()
        for trig in mm_vector.coefficient_list:
            if trig.index > 1:
                pass

if __name__ == '__main__':

    pass
    test = Vector('Iy', True, ',sin(90),cos(2πδIt1),cos(πJt1),cos(180),cos(2πδIt2),cos(πJt2),cos(πJt1)')
    test.str_to_list().list_to_str()
    print(test.symbol, test.coefficient)
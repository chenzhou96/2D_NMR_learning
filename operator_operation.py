import pandas as pd

class Coefficient():
    """
    系数类 包含三角函数类型和自变量
    三角函数为bool类型 0代表cos 1代表sin
    """

    def __init__(self, trig: bool, argu: str, index = 1) -> None:
        self.trig = trig
        self.argu = argu
        self.index = index

class Vector():
    """
    向量类 包含数值,符号,和系数
    符号为bool类型 0代表负 1代表正
    """

    def __init__(self, vector: str, symbol=True, coefficient = '', coefficient_list = list()) -> None:
        self.vector = vector
        self.symbol = symbol
        self.coefficient = coefficient
        self.coefficient_list = coefficient_list

    # 待补充 增加相同Coefficient.trig, Coefficient.argu情况下Coefficient.index的合并
    def str_to_list(self) -> None:
        """
        将Vector.coefficient转换为Vector.coefficient_list
        """

        # 保证Vector.coefficient和Vector.coefficient_list必有一个为空
        if self.coefficient_list:
            print('\n数据报错\n')
            exit()

        coefficients = self.coefficient.split(',')

        trig_list = list() # 中间列表 存储Coefficient类的三角函数
        for coefficient in coefficients:
            if coefficient:
                trig_str, argu = coefficient.split('(') # 注意argu末尾还带着右括号
                trig = trig_str[0] == 's' # 如果是sin则为真 反之为假
                if len(trig_str) == 3: # 区分sin, sin2, sin3...
                    trig_fun = Coefficient(trig, argu[:len(argu)-1])
                else:
                    trig_fun = Coefficient(trig, argu[:len(argu)-1], int(trig_str[-1]))

                if trig_fun.argu == '90' and trig_fun.trig == True:
                    continue
                if trig_fun.argu == '180' and trig_fun.trig == False:
                    self.symbol = not self.symbol
                    continue

                trig_list.append(trig_fun)
        
        self.coefficient_list = trig_list
        self.coefficient = ''

        return None
    
    def list_to_str(self) -> None:
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

        return None

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

def simplify_results(mm_vectors: list) -> list:
    """
    输入宏观磁化矢量组 返回简化后的结果
    """

    # 先拆分 简化 去除掉数值1的表达式
    new_vectors = list()
    for mm_vector in mm_vectors:
        new_vectors

if __name__ == '__main__':

    pass
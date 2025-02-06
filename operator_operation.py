from typing import List, Set
import pandas as pd

class Coefficient:
    """系数类，包含三角函数类型、自变量和幂指数"""

    def __init__(self, trig: bool, argu: str, index: int = 1) -> None:
        self.trig = trig  # True=sin, False=cos
        self.argu = argu  # 自变量
        self.index = index

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coefficient):
            return NotImplemented
        return (self.trig == other.trig
                and self.argu == other.argu
                and self.index == other.index)

    def __hash__(self) -> int:
        return hash((self.trig, self.argu, self.index))

    def __repr__(self) -> str:
        return f"{'sin' if self.trig else 'cos'}({self.argu})^{self.index}"


class Vector:
    """磁化矢量类，包含向量名称、符号、系数和乘数"""

    def __init__(self, vector: str, symbol: bool = True, coefficient: str = '', mul: int = 1) -> None:
        self.vector = vector
        self.symbol = symbol  # True=+, False=-
        self.coefficient = coefficient
        self.coefficient_list: List[Coefficient] = []
        self.exist = True
        self.mul = mul

    def str_to_list(self) -> 'Vector':
        """将字符串系数解析为结构化系数列表"""
        if self.coefficient_list:
            raise ValueError("Coefficient list should be empty when parsing string")

        trig_dict = {}
        for part in filter(None, self.coefficient.split(',')):
            if '(' not in part:
                continue

            base, arg_part = part.split('(', 1)
            arg = arg_part.rstrip(')')

            power = 1
            if base[-1].isdigit():
                power = int(base[-1])
                base = base[:-1]

            trig_type = base.startswith('sin')
            key = (trig_type, arg)

            if arg == '90' and trig_type:
                continue
            if arg == '180' and not trig_type:
                if power % 2 != 0:
                    self.symbol = not self.symbol
                continue

            trig_dict[key] = trig_dict.get(key, 0) + power

        self.coefficient_list = [
            Coefficient(trig, arg, power)
            for (trig, arg), power in trig_dict.items()
            if power > 0
        ]
        self.coefficient = ''
        return self

    def list_to_str(self) -> 'Vector':
        """将系数列表转换为字符串表示"""
        if self.coefficient:
            raise ValueError("Coefficient string should be empty when building from list")

        parts = []
        for coeff in self.coefficient_list:
            prefix = 'sin' if coeff.trig else 'cos'
            power = str(coeff.index) if coeff.index > 1 else ''
            parts.append(f"{prefix}{power}({coeff.argu})")

        self.coefficient = ','.join(parts)
        self.coefficient_list = []
        return self


def read_table(path: str) -> pd.DataFrame:
    """读取算符运算表"""
    return pd.read_csv(path).set_index('vector')


def well_behaved_vector(table: pd.DataFrame) -> Set[str]:
    """获取所有合法向量"""
    return set(table.index) | set(table.columns)


def operator_calculate(mm_vector: Vector, operator: Vector, table: pd.DataFrame) -> List[Vector]:
    """单个算符作用计算"""
    result = table.at[mm_vector.vector, operator.vector]

    if result == 'E':
        return [Vector(mm_vector.vector, mm_vector.symbol, mm_vector.coefficient, mm_vector.mul)]

    def create_new_vector(base_vec: Vector, add_coeff: str, new_vector: str, new_symbol: bool) -> Vector:
        new_coeff = f"{base_vec.coefficient},{add_coeff}".lstrip(',')
        return Vector(new_vector, new_symbol, new_coeff, base_vec.mul)

    vec1 = create_new_vector(mm_vector, f"cos({operator.coefficient})", mm_vector.vector, mm_vector.symbol)

    if result.endswith('-'):
        vec2 = create_new_vector(mm_vector, f"sin({operator.coefficient})", result[:-1], not mm_vector.symbol)
    else:
        vec2 = create_new_vector(mm_vector, f"sin({operator.coefficient})", result, mm_vector.symbol)

    if operator.coefficient == '90':
        return [vec2]
    if operator.coefficient == '180':
        return [vec1]
    return [vec1, vec2]


def vector_calculate(mm_vectors: List[Vector], operators: List[Vector], table: pd.DataFrame) -> List[Vector]:
    """全流程磁化矢量计算"""
    for operator in operators:
        new_vectors = []
        for vec in mm_vectors:
            new_vectors.extend(operator_calculate(vec, operator, table))
        mm_vectors = simplify_results(new_vectors)
    return mm_vectors


def find_difference(coeff_list1: List[Coefficient], coeff_list2: List[Coefficient]):
    """找出两个系数列表中不同的部分"""
    diff1 = [trig for trig in coeff_list1 if trig not in coeff_list2]
    diff2 = [trig for trig in coeff_list2 if trig not in coeff_list1]
    if len(diff1) == 1 and len(diff2) == 1:
        return diff1[0], diff2[0]
    return None


def apply_formula1_or_3(mm_vector1: Vector, mm_vector2: Vector, trig1: Coefficient, trig2: Coefficient, new_vectors: List[Vector]):
    """应用公式1或公式3"""
    trig1.index -= 2
    trig2.index -= 2
    if mm_vector1.symbol == mm_vector2.symbol:  # 公式1
        if not trig1.index:
            mm_vector1.coefficient_list.remove(trig1)
        if not trig2.index:
            mm_vector2.coefficient_list.remove(trig2)
        if not trig1.index and not trig2.index:
            mm_vector2.exist = False
    else:  # 公式3
        new_coefficient = [coeff for coeff in mm_vector1.coefficient_list if coeff != trig1]
        new_coefficient.append(Coefficient(False, f'2{trig1.argu}'))
        new_vector = Vector(mm_vector1.vector, mm_vector1.symbol, mm_vector1.coefficient, mm_vector1.mul)
        new_vector.coefficient_list = new_coefficient
        new_vectors.append(new_vector)
        if not trig1.index:
            mm_vector1.exist = False
        if not trig2.index:
            mm_vector2.exist = False


def are_coefficients_same(coeff_list1: List[Coefficient], coeff_list2: List[Coefficient]):
    """检查两个系数列表是否相同"""
    return all(trig in coeff_list2 for trig in coeff_list1) and all(trig in coeff_list1 for trig in coeff_list2)


def apply_formula4(mm_vector1: Vector, mm_vector2: Vector):
    """应用公式4"""
    for trig in mm_vector1.coefficient_list:
        trig0 = Coefficient(not trig.trig, trig.argu, trig.index)
        if trig0 in mm_vector1.coefficient_list:
            mm_vector1.coefficient_list.remove(trig)
            mm_vector1.coefficient_list.remove(trig0)
            mm_vector1.coefficient_list.append(Coefficient(True, f'2{trig.argu}', trig.index))
            mm_vector2.exist = False
            break


def simplify_results(mm_vectors: List[Vector]) -> List[Vector]:
    """
    输入宏观磁化矢量组，返回简化后的结果
    """
    # 将字符串形式的矢量转换为列表形式
    for mm_vector in mm_vectors:
        mm_vector.str_to_list()

    flag = True  # 标记是否化简到最简形式
    while flag:
        flag = False
        new_vectors = []  # 临时存储产生的新矢量
        num = len(mm_vectors)

        # 简化公式1和公式3
        for i in range(num):
            mm_vector1 = mm_vectors[i]
            if not mm_vector1.exist:
                continue
            for j in range(i + 1, num):
                mm_vector2 = mm_vectors[j]
                if not mm_vector2.exist or mm_vector1.vector != mm_vector2.vector:
                    continue

                # 检查是否满足公式1或公式3的条件
                diff = find_difference(mm_vector1.coefficient_list, mm_vector2.coefficient_list)
                if diff:
                    trig1, trig2 = diff
                    if trig1.argu == trig2.argu and trig1.index > 1 and trig2.index > 1 and trig1.trig != trig2.trig:
                        # 应用公式1或公式3
                        apply_formula1_or_3(mm_vector1, mm_vector2, trig1, trig2, new_vectors)
                        flag = True

        # 添加新生成的矢量
        if new_vectors:
            mm_vectors.extend(new_vectors)

        # 简化公式2和公式4
        for i in range(num):
            mm_vector1 = mm_vectors[i]
            if not mm_vector1.exist:
                continue
            for j in range(i + 1, num):
                mm_vector2 = mm_vectors[j]
                if not mm_vector2.exist or mm_vector1.vector != mm_vector2.vector:
                    continue

                # 检查是否满足公式2或公式4的条件
                if are_coefficients_same(mm_vector1.coefficient_list, mm_vector2.coefficient_list):
                    if mm_vector1.symbol != mm_vector2.symbol:
                        # 应用公式2
                        mm_vector1.exist = False
                        mm_vector2.exist = False
                        flag = True
                    else:
                        # 应用公式4
                        apply_formula4(mm_vector1, mm_vector2)
                        flag = True

        # 删除不存在的矢量
        mm_vectors = [mm_vector for mm_vector in mm_vectors if mm_vector.exist]

    # 将列表形式的矢量转换回字符串形式
    for mm_vector in mm_vectors:
        mm_vector.list_to_str()

    return mm_vectors


if __name__ == '__main__':
    test_vec = Vector('Iy', coefficient='sin(90),cos2(2πδIt1),cos(πJt1)')
    test_vec.str_to_list()
    print([(c.trig, c.argu, c.index) for c in test_vec.coefficient_list])
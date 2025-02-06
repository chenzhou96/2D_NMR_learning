import operator_operation as oo
from typing import List
import pandas as pd

class NMRConfig:
    """NMR实验配置参数"""
    def __init__(self):
        # 计算矩阵存储路径
        self.table_path = 'operator_operation_table.csv'
        # 可检测的宏观磁化矢量
        self.detect_vectors = {'Ix', 'Iy', 'Sx', 'Sy'}
        # 定义起始宏观磁化矢量 一般为 Iz
        self.initial_vectors = [oo.Vector('Iz')]
        # 脉冲算符 θIx, θIy: θ为脉冲角度 Ix/Iy为单位算符
        # 在xy平面的转动算符 2πδIt1Iz: δI为I原子核的化学位移 t1为旋转时间
        # 两核的耦合作用算符 πJt2: J为两核的耦合常数 t2为耦合作用时间
        self.operators = [
        oo.Vector('Ix', coefficient='90'),
        oo.Vector('Sx', coefficient='90'),
        oo.Vector('Iz', coefficient='πδIt1'),
        oo.Vector('Sz', coefficient='πδst1'),
        oo.Vector('IzSz', coefficient='[π/2]Jt1'),
        oo.Vector('Ix', coefficient='180'),
        oo.Vector('Sx', coefficient='180'),
        oo.Vector('Iz', coefficient='πδIt1'),
        oo.Vector('Sz', coefficient='πδst1'),
        oo.Vector('IzSz', coefficient='[π/2]Jt1'),
        oo.Vector('Iz', coefficient='2πδIt2'),
        oo.Vector('Sz', coefficient='2πδIt2'),
        oo.Vector('IzSz', coefficient='πJt2'),
        ]

def validate_operators(operators: List[oo.Vector], table: pd.DataFrame) -> None:
    """验证算符有效性"""
    valid_vectors = oo.well_behaved_vector(table)
    for op in operators:
        if op.vector not in valid_vectors:
            raise ValueError(f"非法算符: {op.vector}")

def format_result(result: oo.Vector) -> str:
    """格式化输出结果"""
    symbol = '+' if result.symbol else '-'
    return f"{symbol}{result.coefficient},{result.vector}"

def main():
    config = NMRConfig()
    table = oo.read_table(config.table_path)

    try:
        validate_operators(config.operators, table)
    except ValueError as e:
        print(f"参数错误: {e}")
        return

    results = oo.vector_calculate(config.initial_vectors, config.operators, table)
    detected = [format_result(vec) for vec in results if vec.vector in config.detect_vectors]

    print("\n可检测磁化矢量:" if detected else "\n无可检测磁化矢量")
    for item in detected:
        print(item)

if __name__ == '__main__':
    main()
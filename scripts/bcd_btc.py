from decimal import Decimal


def compute(arr, avg, high, low, amount, cost, mid, h_price, l_price):
    current_price = Decimal(arr[0][2])
    print(f'compute! {len(arr)}')
    print(f'Current Price: {current_price} ')
    # 三小时平均交易价 三小时最高价 2，3，4，5 价  低五个价 仓位  自己的平均成本和中位值，自己交易的最高价和最低价
    # 持仓最高值比 现价高5%，比均值高3%就卖出
    # 持仓最高值比 现价低5%，比均值低3%就买入
    # 买入量根据历史盘口量计算
    if h_price > (current_price * Decimal("1.05")):
        return 1
    if h_price < (current_price * Decimal("0.95")):
        return -1
    return 0

# 超过仓位涨幅 50% 就自动停止
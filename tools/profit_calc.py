def estimate_profit(price: float):
    """
    วิศวกรรมคำนวณกำไรเบื้องต้น:
    - หักค่าน้ำมันประมาณ 40%
    - หักค่าเครดิตจองงาน 50 บาท
    """
    fuel_cost = price * 0.40
    platform_fee = 50
    net_profit = price - fuel_cost - platform_fee
    return net_profit
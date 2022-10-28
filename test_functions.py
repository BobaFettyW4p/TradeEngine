from TradeEngine import Order, buy_order, completed_order, trade_engine, sell_order

def test_trade_engine():
    test_buy_order = Order('Mark','B',int(100),float(100))
    test_sell_order = Order('Mark','S',int(100),float(100))
    assert trade_engine([test_buy_order],[],[],[]) == buy_order([test_buy_order],[],[],[])
    assert trade_engine([test_sell_order],[],[],[]) == sell_order([test_sell_order],[],[],[])


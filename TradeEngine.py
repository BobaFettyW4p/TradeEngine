from dataclasses import dataclass
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import csv
import time

#the Order dataclass will be used for all unprocessed orders
@dataclass
class Order:
    party: str
    order_type: str
    order_amount: int
    purchase_price: float

#the completed_order dataclass will contain matched and completed orders
@dataclass
class completed_order:
    party: str
    order_type: str
    order_amount: int
    purchase_price: float
    counterparty: str

    def __init__(self,party:str,order_type:str,order_amount:int,purchase_price:float,counterparty:str):
        self.party=party
        self.order_type=order_type
        self.order_amount=order_amount
        self.purchase_price=purchase_price
        self.counterparty=counterparty

#opens a prompt to select an appropriate CSV, imports the data and creates a list of Order class objects
def data_import():
    raw_data, data =[],[]
    Tk().withdraw()
    filename=askopenfilename()
    f = open(filename)
    csv_reader= csv.reader(f)
    for line in csv_reader:
        raw_data.append(line)
    for datum in raw_data:
        object=Order(datum[0],datum[1],int(datum[2]),float(datum[3]))
        data.append(object)
    return data


#verifies that the imported data was imported correctly and conforms to expected standards; errors and quits otherwise
def data_verification(data):
    for position, object in enumerate(data):
        if type(object.party) != str:
            print(
                f"Name field in column {position+1} is type {type(object.party)}. It should be a string, please revise your inputs and try again")
            exit()
        if (object.order_type != "B") and (object.order_type != "S"):
            print(
                f"Buy/Sell field in column {position+1}({object.buy_order}) is not valid. It is '{object.buy_order}' when it should be either 'B' (for a buy order) or 'S' (for a sell order)")
            exit()
        if type(object.order_amount)!= int:
            print(
                f"Order quantity field in column {position+1} is not valid. It is {type(object.order_amount)} when it should be an int. Please revise your inputs and try again")
            exit()
        if type(object.purchase_price)!=float:
            print(
                f"Order price field in column {position+1} is not valid. It is {type(object.purchase_price)} when it should be an int. Please revist your inputs and try again")
            exit()
    print("Data verification process complete. Commencing trade engine")
        

#processes buy orders
def buy_order(order,ledger,buyResting,sellResting):
    #if there are no resting orders to be compared to, just add the order to resting and move on
    if len(sellResting)==0:
        print(
            f"no match for {order} found (sellResting empty). adding to buy resting.")
        buyResting.append(order)
        buyResting.sort(reverse=True, key=lambda x: x.purchase_price)
    for position,sellOrder in enumerate(sellResting):
        if sellOrder.purchase_price > order.purchase_price and (len(sellResting)==position+1):
            #this is a final catch, if the last item in resting isn't a match, add the active order to resting and return
            print(f'No matches for {order} in sellResting. Adding to buyResting.')
            buyResting.append(order)
            buyResting.sort(reverse=True, key=lambda x: x.purchase_price)
            return ledger,buyResting,sellResting
        elif sellOrder.purchase_price > order.purchase_price:
            #if the purchase price of the sell order is higher than that of the buy order, it's not a match
            print(f'No match between {order} and {sellOrder}. Continuing...')
            continue
        elif sellOrder.purchase_price<=order.purchase_price:
            #if this is tripped, the active order has matched with a 
            #several use cases under thisif statement:
            #if both quantities are equal, pretty simple to fill the order and drop both off
            #if the resting order is greater, fill the active order and reduce the quantity in the resting order accordingly
            #finally, if the active order is greater, fill the order, remove the resting order, then continue iterating on the active order
            if sellOrder.order_amount==order.order_amount:
                print(f'Match between {order} and {sellOrder} found. Fultilling order...')
                orderFinal=completed_order(order.party,order.order_type,order.order_amount,order.purchase_price,sellOrder.party)
                sellOrderFinal=completed_order(sellOrder.party,sellOrder.order_type,sellOrder.order_amount,sellOrder.purchase_price,order.party)
                ledger.extend([orderFinal,sellOrderFinal])
                sellResting.remove(sellOrder)
                return ledger,sellResting
            elif order.order_amount<sellOrder.order_amount:
                print(f'Match found between {order} and {sellOrder} found. fulfilling order...')
                orderFinal=completed_order(order.party,order.order_type,order.order_amount,sellOrder.purchase_price,sellOrder.party)
                sellOrderFinal=completed_order(sellOrder.party,sellOrder.order_type,order.order_amount,sellOrder.purchase_price,order.party)
                ledger.extend([orderFinal,sellOrderFinal])
                sellOrder.order_amount-=order.order_amount
                return ledger,sellResting
            elif order.order_amount > sellOrder.order_amount:
                print(f'Match found between {order} and {sellOrder}. Fulfilling...')
                orderFinal=completed_order(order.party,order.order_type,sellOrder.order_amount,sellOrder.purchase_price,sellOrder.party)
                sellOrderFinal=completed_order(sellOrder.party,sellOrder.order_type,sellOrder.order_amount,sellOrder.purchase_price,order.party)
                ledger.extend([orderFinal,sellOrderFinal])
                order.order_amount-=sellOrder.order_amount
                buy_order(order,ledger,buyResting,sellResting)

#processes sell orders; nearly identical logic but inverted
def sell_order(order,ledger,buyResting,sellResting):
    if len(buyResting)==0:
        print(f'No match for {order} (buy resting empty). Adding to sell resting.')
        sellResting.append(order)
        sellResting.sort(key=lambda x: x.purchase_price)
        return sellResting
    for position, buyOrder in enumerate(buyResting):
        if (buyOrder.purchase_price<order.purchase_price) and len(buyResting)==position+1:
            print(f'No matches for {order} in buyResting. Adding to sellResting.')
            sellResting.append(order)
            sellResting.sort(key=lambda x: x.purchase_price)
        elif buyOrder.purchase_price<order.purchase_price:
            print(f'{order} and {buyOrder} not a match. Continuing...')
            continue
        elif buyOrder.purchase_price>=order.purchase_price:
            if buyOrder.order_amount==order.order_amount:
                print(f'match found between {order} and {buyOrder}. Filling...')
                orderFinal=completed_order(order.party,order.order_type,order.order_amount,buyOrder.purchase_price,buyOrder.party)
                buyOrderFinal=completed_order(buyOrder.party,buyOrder.order_type,buyOrder.order_amount,buyOrder.purchase_price,order.party)
                ledger.extend([orderFinal,buyOrderFinal])
                buyResting.remove(buyOrder)
                return ledger,buyResting
            elif buyOrder.order_amount > order.order_amount:
                print(f'match found between {order} and {buyOrder}. Filling...')
                orderFinal=completed_order(order.party,order.order_type,order.order_amount,buyOrder.purchase_price,buyOrder.party)
                buyOrderFinal=completed_order(buyOrder.party,buyOrder.order_type,order.order_amount,buyOrder.purchase_price,order.party)
                ledger.extend([orderFinal,buyOrderFinal])
                buyOrder.order_amount-=order.order_amount
                return ledger,buyResting
            elif buyOrder.order_amount<order.order_amount:
                print(f'match found between {order} and {buyOrder}. Filling order...')
                orderFinal=completed_order(order.party,order.order_type,buyOrder.order_amount,buyOrder.purchase_price,buyOrder.party)
                buyOrderFinal=completed_order(buyOrder.party,buyOrder.order_type,buyOrder.order_amount,buyOrder.purchase_price,order.party)
                ledger.extend([orderFinal,buyOrderFinal])
                buyResting.remove(buyOrder)
                order.order_amount-=buyOrder.order_amount
                sell_order(order,ledger,buyResting,sellResting)


def trade_engine(data,buyResting,sellResting,ledger):
    #iterates/processes every order populated in data using the buy_order and sell_order functions
    for order in data:
        print(f'processing {order}...')
        if order.order_type == 'B':
            print(f'buy order found, running buy_order')
            buy_order(order,ledger,buyResting,sellResting)
        elif order.order_type=='S':
            print(f'sell order found, running sell_order')
            sell_order(order,ledger,buyResting,sellResting)

#exports completed data to a CSV for analysis
def data_export(ledger):
    currentTime = time.strftime("%m-%d-%y-%H-%M-%S")
    csvExport=f'TradeLedger{currentTime}.csv'
    header=['Party','Side','Size','Price','Counterparty']
    print(f'writing to {csvExport}')
    print(f'ledger is {ledger}')
    with open(csvExport,mode='w',newline='') as f:
        write = csv.writer(f,quoting=csv.QUOTE_ALL)
        write.writerow(header)
        for item in ledger:
            write.writerow([item.party, item.order_type,item.order_amount,item.purchase_price,item.counterparty])
    print(f'write successful, please open the file to view results')


if __name__ == '__main__':
    ledger,buyResting,sellResting= [],[],[]
    data=data_import()
    data_verification(data)
    trade_engine(data,buyResting,sellResting,ledger)
    data_export(ledger)
live_trade = True
asset = ["DOGE", "ETH", "BNB", "CAKE", "SUSHI", "LINK", "ADA", "XRP"]
base  = "BTC"
core  = 0.005
margin_percentage = 4
pair,round_off = [], []

for coin in base:
    if coin == "USDT": decimal = 2
    elif coin == "BTC": decimal = 6
    elif coin == "ETH": decimal = 5
    elif coin == "BNB": decimal = 3
    else: decimal == 4
    round_off.append(decimal)

for i in range(len(asset)):
    pair.append(asset[i] + base)

try:
    import os
    import socket
    import requests
    import urllib3
    from datetime import datetime
    from termcolor import colored
    from binance.client import Client
    from binance.exceptions import BinanceAPIException
    from apscheduler.schedulers.blocking import BlockingScheduler

    # Get environment variables
    api_key     = os.environ.get('API_KEY')
    api_secret  = os.environ.get('API_SECRET')
    client      = Client(api_key, api_secret)

    def record_tmp(i):
        if not os.path.exists("core_number"): os.makedirs("core_number")
        with open((os.path.join("core_number", pair[i] + ".txt")), "w", encoding="utf-8") as timestamp_record:
            timestamp_record.write(str(core))

    def retrieve_tmp(i):
        with open((os.path.join("core_number", pair[i] + ".txt")), "r", encoding="utf-8") as timestamp_record:
            return float(timestamp_record.read())

    # Record the core number before running
    for i in range(len(pair)): record_tmp(i)
    
    def buy_low_sell_high():
        for i in range(len(pair)):
            my_core_number  = retrieve_tmp(i)
            asset_info      = client.get_symbol_ticker(symbol=pair[i])
            asset_price     = float(asset_info.get("price"))
            asset_balance   = float(client.get_asset_balance(asset=asset[i]).get("free"))

            current_core    = round(asset_balance * asset_price, round_off[i])
            change_percent  = round(((current_core - my_core_number) / my_core_number * 100), 4)
            trade_amount    = round(abs(current_core - my_core_number), round_off[i])

            if (current_core > my_core_number) and (abs(change_percent) > margin_percentage):
                if live_trade: client.order_market_sell(symbol=pair[i], quoteOrderQty=trade_amount)
                print(colored(asset_info, "green"))
                print(colored("Created at           : " + str(datetime.today().strftime("%d-%m-%Y @ %H:%M:%S")), "green"))
                print(colored("Prefix Core          : " + str(my_core_number) + " " + base, "green"))
                print(colored("Current Core         : " + str(current_core) + " " + base, "green"))
                print(colored("Percentage Changed   : " + str(change_percent) + " %", "green"))
                print(colored("Action               : SELL " + str(trade_amount) + " " + base + "\n", "green"))

            elif (current_core < my_core_number) and (abs(change_percent) > margin_percentage):
                record_tmp(my_core_number + (core * 0.05))
                if live_trade: client.order_market_buy(symbol=pair[i], quoteOrderQty=trade_amount)
                print(colored(asset_info, "red"))
                print(colored("Created at           : " + str(datetime.today().strftime("%d-%m-%Y @ %H:%M:%S")), "red"))
                print(colored("Prefix Core          : " + str(my_core_number) + " " + base, "red"))
                print(colored("Current Core         : " + str(current_core) + " " + base, "red"))
                print(colored("Percentage Changed   : " + str(change_percent) + " %", "red"))
                print(colored("Action               : BUY " + str(trade_amount) + " " + base + "\n", "red"))

            else:
                print(asset_info)
                print("Created at           : " + str(datetime.today().strftime("%d-%m-%Y @ %H:%M:%S")))
                print("Prefix Core          : " + str(my_core_number) + " " + base)
                print("Current Core         : " + str(current_core) + " " + base)
                print("Percentage Changed   : " + str(change_percent) + " %")
                print("Action               : Do Nothing\n")

    try:
        scheduler = BlockingScheduler()
        if live_trade: scheduler.add_job(buy_low_sell_high, 'cron', minute='0')
        else: scheduler.add_job(buy_low_sell_high, 'interval', seconds=3)
        scheduler.start()
    except (KeyError,
            socket.timeout,
            BinanceAPIException,
            ConnectionResetError,
            urllib3.exceptions.ProtocolError,
            urllib3.exceptions.ReadTimeoutError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout) as e:

        print(e)
        # if not os.path.exists("Error_Message"): os.makedirs("Error_Message")
        # with open((os.path.join("Error_Message", config.pair + ".txt")), "a") as error_message:
        #     error_message.write("[!] " + config.pair + " - " + "Created at : " + datetime.today().strftime("%d-%m-%Y @ %H:%M:%S") + "\n")
        #     error_message.write(str(e) + "\n\n")

except KeyboardInterrupt: print("\n\nAborted.\n")

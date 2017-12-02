import csv
import datetime
import logging
import unittest
import argparse
import pickle 
import glob



class Client():

	def __init__(self, name, instruments={}, balance=1000):
		self.name = name
		self.instruments = instruments
		self.balance = balance


	def update_instrument(self, instrument, quantity, buy_sell):
		if buy_sell == "buy":
			return None

		elif buy_sell == "sell":
			return None

	def change_balance(self, balance):
		""" Accepts negative numbers"""
		self.balance = self.baland + balance


	def trade_log(self, file, logs):
		client_log = open(name+".log", "a")
		for line in logs:

			client_log.write(line)


  
class Market():
	""" A class that manages Trades, Time and Files"""

	def __init__(self, Clients=[]):
		self.clients = []
		self.trades = []
		self.trade_id_count = 1
		self.days_traded = set()
		self.traded_instruments = set()

	def add_new_client(self, name, instruments, balance):
		clients.append(Client(name, instruments, balance))


	def process_all_trades(self, csv_file_list, store_file=False):
		#trade_list = [] #all trades in csv files
		
		for file in csv_file_list:
			with open(file, "rU") as csv_file:
				csv_reader = csv.reader(csv_file, delimiter=",")

				# Check if main 4 parameters are inputed?

				for row in csv_reader:
					instrument = row[0]
					price = float(row[1])
					quantity = float(row[2])
					timestamp =  datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")

					#Optional columns
					try:
						trade_reference = row[4]
					except IndexError:
						trade_reference = None
					try:
						instrument_type = row[5]
					except IndexError:
						instrument_type = None

					try:
						underlying_asset = row[6]
					except IndexError:
						underlying_asset = None

					try:
						client_reference = row[7]
					except IndexError:
						client_reference = None


					self.days_traded.add(timestamp.date()) #datetime objects
					self.traded_instruments.add(instrument)

					
					self.trades.append(Trade(self.trade_id_count, instrument, price, quantity, timestamp, trade_reference, instrument_type,underlying_asset, client_reference)) #create and append Trade to list
					logging.info('{} - Imported Trade: ID: {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.trade_id_count))

					self.trade_id_count += 1

			csv_file.close()

		if store_file:
			i = len(glob.glob("local_storage/*")) + 1
			store_in_file = open("local_storage/trades{}.obj".format(str(i)), 'w') #Stores processed objects into a file
			pickle.dump(self.trades, store_in_file) 
			store_in_file.close()

		return self.trades


	def days_with_trades(self):
		""" The days in which trades were conducted. 
		    Returns a set of datetime objects """
		return self.days_traded


	def trades_by_date(self, date): 
		"""Get trades that match a certain date. Must match format YYYY-MM-DD"""
		trades_on_date = []

		for trade in self.trades:
			day = datetime.datetime.strptime(date, "%Y-%m-%d").date()
			if trade.get_date() == day:
				trades_on_date.append(trade)

		return trades_on_date



	def traded_instruments(self):
		return self.traded_instruments


	def report(self, day=None):
		""" """
		days_traded_dic = dict((x,[]) for x in self.days_traded)

		return None
		#for day in self.days_traded:



		#daily_total_trade_value
		#daily_closing_value
		#daily_closing_position

		#total trade value
		#closeing value
		#closing position

	def daily_total_trade_value(self, day):
		if day is str: #convert string to datetime object if string is given
			day = datetime.datetime.strptime(day, "%Y-%m-%d").date()

		total_traded_value = 0
		for trade in self.trades_by_date(day):
			total_traded_value += (trade.price * trade.quantity)


	def daily_closing_value(self):
		return self.trades_by_date(day)[-1].price

	def daily_closing_position(self):
		total_quantity = 0
		for trade in self.trades_by_date(day):
			total_quantity += trade.quantity 

	def get_constituent_trades(self, trade_reference):
		""" Returns trades that share a certain trade reference"""
		consituent_trades = []
		for trade in self.trades:
			print trade.trade_reference == trade_reference
			if trade.trade_reference == trade_reference:
				consituent_trades.append(trade)

		return consituent_trades

	# def load_pickle_files(self):
	# 	for file in glob.glob("local_storage/*"):
	# 		f = open(file, 'r') 
	#  		trade_obj = pickle.load(f)
	#  		print trade_obj
	# 	 	for obj in trade_obj:
	# 	 		self.trades.append(obj)


class Trade():
	""" A class that represents a single trade"""

	def __init__(self, id, instrument, price, quantity, timestamp, trade_reference=None, instrument_type=None, underlying_asset=None, client_reference=None):
		self.id = id
		self.instrument = instrument
		self.price = price
		self.quantity = quantity
		self.timestamp = timestamp
		self.trade_reference = trade_reference
		self.instrument_type = instrument_type
		self.underlying_asset = underlying_asset
		self.client_reference = client_reference


	def get_market_value(self):
		return self.price * self.quantity

	def get_instrumnet(self):
		return self.instrument

	def get_price(self):
		return self.price

	def get_quantity(self):
		return self.quantity

	def get_timestamp(self):
		return self.timestamp

	def get_date(self):
		return self.timestamp.date()

	def get_optional(self):
		return self.optional

	# def __str__():
	# 	return None


# class Instrument():
# 	"""A class for instruments"""

# 	def __init__(self, instrument, price, trade_time):
# 		self.something = 1

# 	# def __init__(self, total_market_value, closing_value, average_price_per_day):
# 	# 	self.total_market_value = total_market_value
# 	# 	self.closing_value = closing_value
# 	# 	self.average_price_per_day = average_price_per_day




def main():
	parser = argparse.ArgumentParser(description='Process Trades')
	parser.add_argument('-f', '--file', help='Path to file. Example: "file.csv" ', type=str, dest="file")
	parser.add_argument('-d', '--directory', help='File list: example "[file1, file2, ]"', type=str, dest="directory")
	parser.add_argument('-s', '--store', help="If", dest="store", action='store_true')

	args = parser.parse_args()

	client1 = Client("John Doe")

	market = Market([client1])
	

	if args.file:
		trades = market.process_all_trades([args.file], args.store)
	elif args.directory:
		trades = market.process_all_trades(glob.glob(args.directory+"/*"), args.store)
	else:
		print "No input file"

	#print eval(args.files)

	market.report()


	#print market.get_constituent_trades("optional1")
	#trades = market.process_all_trades(["sample.csv"])
	

	#print market.get_constituent_trades(1)
	#print trades[0].get_date()
	#print market.get_trades_by_date("2017-11-11")


	#print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# class TestAnagrams(unittest.TestCase):

#     def test_anagrams(self):
#         anagrams = Anagrams()
#         self.assertEquals(anagrams.get_anagrams('plates'), ['palest', 'pastel', 'petals', 'plates', 'staple'])
#         self.assertEquals(anagrams.get_anagrams('eat'), ['ate', 'eat', 'tea'])





if __name__ == "__main__":
    main()
    #unittest.main()



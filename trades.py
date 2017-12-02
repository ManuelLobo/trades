import csv
import datetime
import logging
import unittest
import argparse
import pickle 
import glob


  
class Market():

	def __init__(self):
		self.trades = []
		self.trade_id_count = 1

	def process_all_trades(self, csv_file_list, store_file=False):
		#trade_list = [] #all trades in csv files
		for file in csv_file_list:
			with open(file, "rU") as csv_file:
				csv_reader = csv.reader(csv_file, delimiter=",")
				for row in csv_reader:
					instrument = row[0]
					price = float(row[1])
					quantity = float(row[2])
					timestamp =  datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
					#optional = row[4:]

					
					self.trades.append(Trade(self.trade_id_count, instrument, price, quantity, timestamp)) #create and append Trade to list
					logging.warning('{} - Imported Trade: ID: {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.trade_id_count))

					self.trade_id_count += 1

			csv_file.close()

		if store_file:
			i = len(glob.glob("local_storage/*")) + 1
			store_in_file = open("local_storage/trades{}.obj".format(str(i)), 'w') #Stores processed objects into a file
			pickle.dump(self.trades, store_in_file) 
			store_in_file.close()

		return self.trades

	def get_trades_by_date(self, date): 
		"""Get trades that match a certain date. Must match format YYYY-MM-DD"""
		trades_per_date = []

		for trade in self.trades:
			day = datetime.datetime.strptime(date, "%Y-%m-%d").date()
			if trade.get_date() == day:
				trades_per_date.append(trade)

		return trades_per_date

	def get_total_trade_value(self):
		return None


	def get_closing_value(self):
		return None

	def get_closing_position(self):
		return None

	# def get_constituent_trades(self, trade_reference):
	# 	consituent_trade_references = []
	# 	dic = {}
	# 	for trade in self.trades:
	# 		try:
	# 			dic[trade.instrument].append(trade.reference)
	# 		except KeyError:
	# 			dic[trade.instrument] = []
	# 			dic[trade.instrument].append(trade.reference)

	# 	for ins in dic:
	# 		if trade_reference in dic[ins]:
	# 			return dic[ins]

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


class Instrument():
	"""A class for instruments"""

	def __init__(self, total_market_value, closing_value, average_price_per_day):
		self.total_market_value = total_market_value
		self.closing_value = closing_value
		self.average_price_per_day = average_price_per_day





def main():
	parser = argparse.ArgumentParser(description='Process Trades')
	parser.add_argument('-f', '--file', help='Path to file. Example: "file.csv" ', type=str, dest="file")
	parser.add_argument('-d', '--directory', help='File list: example "[file1, file2, ]"', type=str, dest="directory")
	parser.add_argument('-s', '--store', help="If", dest="store", action='store_true')

	args = parser.parse_args()

	market = Market()

	if args.file:
		trades = market.process_all_trades([args.file], args.store)
	elif args.directory:
		trades = market.process_all_trades(glob.glob(args.directory+"/*"), args.store)
	else:
		print "No input file"

	#print eval(args.files)


	
	#trades = market.process_all_trades(["sample.csv"])
	

	#print market.get_constituent_trades(1)
	#print trades[0].get_date()
	#print market.get_trades_by_date("2017-11-11")


	#print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")



if __name__ == "__main__":
    main()

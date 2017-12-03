import csv
import datetime
import logging
import unittest
import argparse
import pickle 
import glob

class Market():

	def __init__(self):
		self.client_list = []

	def add_new_client(self, Client):
		""" Add a Client Object"""
		self.client_list.append(Client)
		logging.info("New client added with id: {}".format(Client.client_id))


class Client():
	def __init__(self, client_id):
		self.client_id = client_id
		self.balance = 1000
		self.instruments = {}

		self.trades = []
		self.trade_id_count = 1
		
		self.days_traded = set()
		self.instruments_traded = {}
		

	def get_balance(self):
		return self.balance

	def get_instruments(self):
		return self.instruments

	def change_instrument(self, instrument, quantity):
		""" Accepts negative numbers"""	

		try: #try to add quantity if instrument exists
			self.instruments[instrument] += quantity
		except KeyError: #If instrument does not exist
			self.instruments[instrument] = quantity

		
		if self.instruments[instrument] <= 0: #If quantity of instrument reaches zero, remove it
			del self.instruments[instrument]




	def change_balance(self, balance):
		""" Accepts negative numbers"""
		self.balance = self.balance - balance


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


					self.change_balance(price*quantity)
					self.change_instrument(instrument, quantity)

					#get instrument trading information
					try:
						self.instruments_traded[instrument].append((price, quantity, timestamp))
					except KeyError:
						self.instruments_traded[instrument] = []
						self.instruments_traded[instrument].append((price, quantity, timestamp))
				
					self.trades.append(Trade(self.trade_id_count, self.client_id, instrument, price, quantity, timestamp, trade_reference, instrument_type,underlying_asset, client_reference)) #create and append Trade to list
					

					logging.info('{} - Imported Trade: ID: {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.trade_id_count))

					self.trade_id_count += 1

			csv_file.close()

		# if store_file:
		# 	i = len(glob.glob("local_storage/*")) + 1
		# 	store_in_file = open("local_storage/trades{}.obj".format(str(i)), 'w') #Stores processed objects into a file
		# 	pickle.dump(self.trades, store_in_file) 
		# 	store_in_file.close()

		return self.trades


	def days_with_trades(self):
		""" The days in which trades were conducted. 
		    Returns a set of datetime objects """
		return self.days_traded


	def trades_by_date(self, day): 
		"""Get trades that match a certain date. Must match format YYYY-MM-DD"""
		trades_on_date = []

		for trade in self.trades:
			#day = datetime.datetime.strptime(date, "%Y-%m-%d").date()
			if trade.get_date() == day:
				trades_on_date.append(trade)

		return trades_on_date


	def daily_total_trade_value(self, day):
		if day is str: #convert string to datetime object if string is given
			day = datetime.datetime.strptime(day, "%Y-%m-%d").date()

		total_traded_value = 0
		for trade in self.trades_by_date(day):
			total_traded_value += (trade.price * trade.quantity)

		return total_traded_value


	def daily_closing_value(self, day):
		return self.trades_by_date(day)[-1].price

	def daily_closing_position(self, day):
		total_quantity = 0
		for trade in self.trades_by_date(day):
			total_quantity += trade.quantity 

		return total_quantity

	def get_constituent_trades(self, trade_reference):
		""" Returns trades that share a certain trade reference"""
		consituent_trades = []
		for trade in self.trades:
			print trade.trade_reference == trade_reference
			if trade.trade_reference == trade_reference:
				consituent_trades.append(trade)

		return consituent_trades

	def get_instrument_info(self):

		for day in sorted(self.days_traded):
			#day = datetime.datetime.strptime(day, "%Y-%m-%d").date()
			for instrument in sorted(self.instruments_traded):
				number_of_trades = 0
				trade_flag = False
				closing_value = 0
				total_market_value = 0

				for trade in self.instruments_traded[instrument]:
					#print trade, instrument, number_of_trades, day, trade[2]
					if day == trade[2].date():
						trade_flag = True
						number_of_trades += 1
						closing_value = trade[0]
						total_market_value += trade[0]*trade[1]

				if trade_flag:
					average_price_per_day = total_market_value/number_of_trades
				else:
					average_price_per_day = None		

				print "Report from {} for {}".format(day, instrument)
				print "Total market value for instrument {}: {}".format(instrument, total_market_value)
				print "Closing value for instrument {}: {}".format(instrument, closing_value)
				print "Average price per day for instrument {}: {}".format(instrument, average_price_per_day)
				print "\n\n\n\n"

	

	def daily_report(self, single_day=None):
		""" """
		#days_traded_dic = dict((x,[]) for x in self.days_traded)
		single_day = datetime.datetime.strptime(single_day, "%Y-%m-%d").date()
		if not single_day:
			for day in self.days_traded:
				print "Report from {}".format(day)
				print "Total trade value: {}".format(self.daily_total_trade_value(day))
				print "Closing value: {}".format(self.daily_closing_value(day))
				print "Closing position: {}".format(self.daily_closing_position(day))
				print "\n\n\n\n"
		else:
			print "Report from {}".format(single_day)
			print "Total trade value: {}".format(self.daily_total_trade_value(single_day))
			print "Closing value: {}".format(self.daily_closing_value(single_day))
			print "Closing position: {}".format(self.daily_closing_position(single_day))
			print "\n\n\n\n"

		#for day in self.days_traded:



		#daily_total_trade_value
		#daily_closing_value
		#daily_closing_position

		#total trade value
		#closeing value
		#closing position


	# def load_pickle_files(self):
	# 	for file in glob.glob("local_storage/*"):
	# 		f = open(file, 'r') 
	#  		trade_obj = pickle.load(f)
	#  		print trade_obj
	# 	 	for obj in trade_obj:
	# 	 		self.trades.append(obj)


class Trade():
	""" A class that represents a single trade"""

	def __init__(self, trade_id, client_id, instrument, price, quantity, timestamp, trade_reference=None, instrument_type=None, underlying_asset=None, client_reference=None):
		self.trade_id = trade_id
		self.client_id = client_id
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

	market = Market() 
	client = Client("client01")
	market.add_new_client(client)
	

	if args.file:
		trades = client.process_all_trades([args.file], args.store)
	elif args.directory:
		trades = client.process_all_trades(glob.glob(args.directory+"/*"), args.store)
	else:
		logging.warning("No input file")

	#print eval(args.files)

	#client.daily_report("2017-11-15")
	print client.get_instrument_info()


	#print client.get_constituent_trades("optional1")
	#trades = client.process_all_trades(["sample.csv"])
	

	#print client.get_constituent_trades(1)
	#print trades[0].get_date()
	#print client.get_trades_by_date("2017-11-11")


	#print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# class TestAnagrams(unittest.TestCase):

#     def test_anagrams(self):
#         anagrams = Anagrams()
#         self.assertEquals(anagrams.get_anagrams('plates'), ['palest', 'pastel', 'petals', 'plates', 'staple'])
#         self.assertEquals(anagrams.get_anagrams('eat'), ['ate', 'eat', 'tea'])


	# if store_file:
	# 	i = len(glob.glob("local_storage/*")) + 1
	# 	store_in_file = open("local_storage/trades{}.obj".format(str(i)), 'w') #Stores processed objects into a file
	# 	pickle.dump(self.trades, store_in_file) 
	# 	store_in_file.close()




if __name__ == "__main__":
    main()
    #unittest.main()



import csv
import datetime
import logging
import argparse
import pickle 
import glob

class Market():
	""" A class that manages different users """

	def __init__(self):
		self.client_list = []

	def add_new_client(self, Client):
		""" 
		Creates a new client.
		
		Keyword arguments:
		Client -- Client object.
		"""

		self.client_list.append(Client)
		logging.info("New client added with id: {}".format(Client.client_id))


class Client():
	""" 
	A class that manages trades, instruments and balance of a certain client. 
	As a default, clients have an initial balance of 1000 and no instruments.
	"""

	def __init__(self, client_id):
		""" 
		Constructor for the Client Object.

		Keyword arguments:
		client_id -- a str for a client ID.

		"""
		self.client_id = client_id
		self.balance = 1000
		self.instruments = {}

		self.trades = []
		self.trade_id_count = 1
		
		self.days_traded = set()
		self.instruments_traded = {}
		

	def get_balance(self):
		""" Returns the client's balance """

		return self.balance


	def get_instruments(self):
		""" Returns the client's instruments and each of their quantities """

		return self.instruments


	def change_instrument(self, instrument, quantity):
		""" 
		Changes the instruments depending if there an instrument was bought or sold.
		
		Keyword Arguments:
		instrument -- a str for an instrument
		quantity -- an int for the quantity
		"""	

		try: #try to add quantity if instrument exists
			self.instruments[instrument] += quantity
			logging.info("Intrument ({}) quantity Change: {}".format(instrument, quantity))
		except KeyError: #If instrument does not exist
			self.instruments[instrument] = quantity
			logging.info("Intrument ({}) quantity Change: {}".format(instrument, quantity))

		
		if self.instruments[instrument] <= 0: #If quantity of instrument reaches zero, remove it
			del self.instruments[instrument]
			logging.info("Removed instrument {} from Client {} , Quantity: {}".format(instrument, self.client_id, quantity))


	def change_balance(self, balance):
		""" 
		Changes the balance depending if there an instrument was bought or sold.
		
		Keyword Arguments:
		balance -- an int for the balance to be changed
		"""	

		self.balance = self.balance - balance
		logging.info("Balance change: {}  |  Current Balance: {}".format(balance, self.balance))


	def process_all_trades(self, csv_file_list):
		""" 
		Processes all the trades that are inside an input csv file.
		Creates a Trade Object for each trade that is processed, alters the Client's balance,
		and updates the Client's Instruments.
		
		Keyword Arguments:
		csv_file_list -- a list of input files (list of strings)
		store_file -- a Boolean to determine whether store processed information locally.
		"""	
		#trade_list = [] #all trades in csv files
		for file in csv_file_list:
			with open(file, "rU") as csv_file:
				csv_reader = csv.reader(csv_file, delimiter=",")
				for row in csv_reader:
					#Main columns
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
				
					self.trades.append(Trade(self.trade_id_count, self.client_id, instrument, price, quantity, timestamp, trade_reference, instrument_type,underlying_asset, client_reference))
					self.trade_id_count += 1
					logging.info('Processed traded with ID {}: | Instrument: {} | Price: {} | Quantity: {} | Date: {}'.format(self.trade_id_count, instrument, price, quantity, timestamp))
					
			csv_file.close()

		return self.trades


	def trades_market_value(self):
		out_file = open("outputs/all_trades_market_value.log", "w")
		for trade in self.trades:
			out_file.write("{} | Market Value: {}\n".format(str(trade), str(trade.get_market_value())))

		out_file.close()


	def days_with_trades(self):
		""" The days in which trades were conducted. 
		    Returns a set of datetime objects """
		return self.days_traded


	def trades_by_date(self, day): 
		"""Get trades that match a certain date.

		Keyword Arguments:
		day -- is a Datetime.date() object
		"""
		trades_on_date = []

		for trade in self.trades:
			if trade.get_date() == day:
				trades_on_date.append(trade)

		return trades_on_date


	def daily_total_trade_value(self, day):
		""" 
		The total value of the trades that were made during a specific day.

		Keyword Arguments:
		day -- is a Datetime.date() object (string accepted)
		"""

		if day is str: #convert string to datetime object if string is given
			day = datetime.datetime.strptime(day, "%Y-%m-%d").date()

		total_traded_value = 0
		for trade in self.trades_by_date(day):
			total_traded_value += (trade.price * trade.quantity)

		return total_traded_value


	def daily_closing_value(self, day):
		""" The price of the last trade """

		return self.trades_by_date(day)[-1].price


	def daily_closing_position(self, day):
		""" The total quantity of instruments traded """

		total_quantity = 0
		for trade in self.trades_by_date(day):
			total_quantity += trade.quantity 

		return total_quantity


	def get_constituent_trades(self, trade_reference):
		""" 
		Returns trades that share a certain trade reference

		Keyword Arguments:
		trade_reference -- is a str of the trade reference
		"""

		out_file = open("outputs/constituent_trades_ref_{}.log".format(trade_reference), "w")
		consituent_trades = []
		for trade in self.trades:
			if trade.trade_reference == trade_reference:
				out_file.write(str(trade)+"\n")
				consituent_trades.append(trade)
		out_file.close()
		return consituent_trades


	def get_instrument_info(self):
		"""
		Writes to a file the total market value, the closing value, 
		and average price per day, for each of the instruments.
		
		Keyword Arguments:
		output_file -- a str for the path to the output_file
		"""

		out_file = open("outputs/instrument_info.log", "w")
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

				out_file.write("Report from {} for {}\n".format(day, instrument))
				out_file.write("Total market value for instrument {}: {}\n".format(instrument, total_market_value))
				out_file.write("Closing value for instrument {}: {}\n".format(instrument, closing_value))
				out_file.write("Average price per day for instrument {}: {}\n\n".format(instrument, average_price_per_day))
		out_file.close()

	

	def daily_report(self, single_day=None):
		"""
		Writes to a file the total traded value, closing value, and the closing position,
		for every day on which there were trades, or for a specific day.
		
		Keyword Arguments:
		single_day -- a str of the date in format YYYY-MM-DD (Default: None)
		output_file -- a str for the path to the output_file
		"""

		out_file = open("outputs/daily_report.log", "w")
		if not single_day:
			for day in self.days_traded:
				out_file.write("Report from {}\n".format(day))
				out_file.write("Total trade value: {}\n".format(self.daily_total_trade_value(day)))
				out_file.write("Closing value: {}\n".format(self.daily_closing_value(day)))
				out_file.write("Closing position: {}\n\n".format(self.daily_closing_position(day)))
		else:
			single_day = datetime.datetime.strptime(single_day, "%Y-%m-%d").date()
			out_file.write("Report from {}\n".format(single_day))
			out_file.write("Total trade value: {}\n".format(self.daily_total_trade_value(single_day)))
			out_file.write("Closing value: {}\n".format(self.daily_closing_value(single_day)))
			out_file.write("Closing position: {}\n\n".format(self.daily_closing_position(single_day)))

		out_file.close()




class Trade():
	""" A class that represents a single trade"""

	def __init__(self, trade_id, client_id, instrument, price, quantity, timestamp, trade_reference=None, instrument_type=None, underlying_asset=None, client_reference=None):
		""" 
		Constructor for the Trade Object

		Keyword arguments:
		trade_id -- a str for the trade ID
		client_id -- a str for the client ID
		instrument -- a str for the instrument
		price -- an int for the price
		quantity -- an int for the quantity
		timestamp -- a datetime object for the timestamp
		trade_reference -- a str for the trade reference (Default: None)
		instrument_type -- a str for the instrument type (Default: None)
		underlying_asset -- a str for the underlying asset (Default: None)
		client_reference -- a str for the client reference (Default: None)
		"""

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
		"""
		Returns the market value of the trade.
		"""
		return self.price * self.quantity


	def get_instrumnet(self):
		"""
		Returns the trade's instrument.
		"""
		return self.instrument


	def get_price(self):
		"""
		Returns the trade's instrument price.
		"""
		return self.price


	def get_quantity(self):
		"""
		Returns the trade's instrument quantity.
		"""
		return self.quantity


	def get_timestamp(self):
		"""
		Returns the trade's timestamp as a datetime object.
		"""
		return self.timestamp


	def get_date(self):
		"""
		Returns the trade date as a datetime object (format YYYY-MM-DD).
		"""
		return self.timestamp.date()

	def __str__(self):
		return "Trade ID: {} | Client ID: {} | Instrument: {} | Price: {} | Quantity: {} | Timestamp: {}".format(self.trade_id, self.client_id, self.instrument, self.price, self.quantity, self.timestamp)



def main():
	parser = argparse.ArgumentParser(description='Process Trades')
	req_arg = parser.add_argument_group(title='Required Arguments')
	req_arg.add_argument('-c', '--client', help='The Client ID. If client file does not exists, it will create a new file. " ', type=str, dest="client", required=True)
	parser.add_argument('-f', '--file', help='Path to file. Example: "file.csv" ', type=str, dest="file")
	parser.add_argument('-d', '--directory', help='File list: example "[file1, file2, ]"', type=str, dest="directory")
	parser.add_argument('-i', '--instrument', help="Get the total market value, the closing value, and average price per day. Stores in file instrument_info.log ", dest="instrument", action='store_true')
	parser.add_argument('-mv', '--marketvalue', help="Gets market value for every trade. Stores in file all_trades_market_value.log", dest="marketvalue", action='store_true')
	parser.add_argument('-ct', '--cons_trades', help="Gets constituent trades for a certain trade reference and save in outputs/constituent_trades_ref_X.log", dest="cons_trades")
	parser.add_argument('-da', '--daily', help="Total traded value, closing value, and the closing position for each day. Stores in file daily_report.log", dest="daily")
	parser.add_argument('-s', '--store_client', help="Stores client file locally after the processing of the trades.", dest="store_client", action='store_true')
	#parser.add_argument('-cl', '--client_file', help="Loads previously saved Client file. Path to file must be provided", dest="client_file")



	args = parser.parse_args()

	logging.basicConfig(filename='log/trading_events.log',level=logging.DEBUG)

	load_file = False
	if args.client:
		try:
			f = open("clients/{}.obj".format(args.client), 'r') 
			client = pickle.load(f)
			load_file = True
		except IOError: 
			client = Client("client01")


	market = Market() 
	#client = Client("client01")
	market.add_new_client(client)
	
	trades_processed = False
	if args.file:
		trades = client.process_all_trades([args.file])
		trades_processed = True
	elif args.directory:
		trades = client.process_all_trades(glob.glob(args.directory+"/*"))
		trades_processed = True

	elif not args.file and not args.directory and not load_file:
		print "No input file"


	if trades_processed or load_file:
	 	if args.instrument:
	 		client.get_instrument_info()

	 	if args.marketvalue:
	 		client.trades_market_value()

	 	if args.cons_trades:
	 		client.get_constituent_trades(args.cons_trades)

	 	if args.daily:
	 		if args.daily == "all":
	 			args.daily = None
	 		client.daily_report(args.daily)


 	if args.store_client:
 		store_in_file = open("clients/{}.obj".format(args.client), 'w') #Stores processed objects into a file
 		pickle.dump(client, store_in_file) 
 		store_in_file.close()



if __name__ == "__main__":
    main()
    #unittest.main()



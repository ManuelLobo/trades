# trades


Required Arguments:
  -c , --client         The Client ID. If client file does not exists, it will create a new file.
  
optional arguments:
  -h, --help            Show this help message and exit
  -f , --file           Path to file. Example: "file.csv"
  -d , --directory      File list: example "[file1, file2, ]"
  -i, --instrument      Get the total market value, the closing value, and average price per day. Stores in file instruments.log
  -mv, --marketvalue    Gets market value for every trade. Stores in file trades_marketvalue.log
  -ct , --cons_trades   Gets constituent trades for a certain trade reference
  -da, --daily          Total traded value, closing value, and the closing position for each day. Stores in file daily.log
  -s, --store_client    Stores client file locally after the processing of the trades.


To run the program,                        
Commands:


  python trades.py --client client0 --file "sample.csv" --cons_trades "optional1"
  

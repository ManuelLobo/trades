# Trades


#### Required Arguments:
  - -c , --client         The Client ID. If client file does not exists, it will create a new file.
  
#### Optional Arguments:
  - -h, --help            Show this help message and exit
  - -f , --file           Path to file. Example: "file.csv"
  - -d , --directory      File list: example "[file1, file2, ]"
  - -i, --instrument      Get the total market value, the closing value, and average price per day. Stores in file instrument_info.log
  - -mv, --marketvalue    Gets market value for every trade. Stores in file trades_marketvalue.log
  - -ct , --cons_trades   Gets constituent trades for a certain trade reference
  - -da, --daily          Total traded value, closing value, and the closing position for each day. Stores in file daily_report.log
  - -s, --store_client    Stores client file locally after the processing of the trades.


To run the program, at least a Client ID is necessary. If it's the first time running the program, a CSV file must also be provided. If the "store_client" argument is activated, it will store the client file locally after processing. After this, the program can be run without providing a file.

## Example Commands:
*Process trades and save Client object locally* <br />
``` python trades.py --client client0 --file "sample.csv" --store_client```
  
*Get instrument information and save in outputs/instrument_info.log* <br />
``` python trades.py --client client0 --instrument```
    
*Get market value information and save in outputs/trades_marketvalue.log* <br />
``` python trades.py --client client0 --marketvalue```
    
*Get constituent trades information for reference "optional1" and save in outputs/constituent_trades_ref_X.log* <br />
``` python trades.py --client client0 --cons_trades "optional1"```
    
*Get trade details on a specific day and save in outputs/daily_report.log* <br />
```python trades.py --client client0 --daily "2017-11-11"```
 
*Get trade details for all the days and save in outputs/daily_report.log* <br />
```python trades.py --client client0 --daily "all"```


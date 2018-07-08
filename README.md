# Indian-stock-market (Dividend, Bonus, Plan, Demat)

The tool uses plan data (stocks to be acquired) and existing holding (stocks already acquired) to generate Quarterly reports on stocks to be acquired in the quarter with 6-month delay (can be customized).

# AMFI Data
The file data/amfi-data/amfi-\*.csv has a list of companies with market cap and cap type released every 6 months (In July for Jan-Jun).
These are downloaded from the amfi website and processed further.

Fix discrepancy

$ cd src/amfi

$ ./amfi_invoke.sh

Review the generated reports/amfi-reports/\*.csv

The report has important things like ISIN Number, Company name, Company Rank By mcap, mcap (avg of 6 months) and cap type (large, mid cap and small cap).

# ISIN Data

The file data/isin-data/isin-(bse|nse)-500.csv has a list of BSE 500 and NSE 500 companies with ISIN number.
These were downloaded directly from the NSE and BSE websites.

Fix discrepancy

  $ cd src/isin
  
  $ ./isin_invoke.sh
  
Review the generated reports/isin-reports/\*.csv

# PLAN DATA

Prepare data/plan-data/plan-data.csv file

Include weight for each company and cummulative weight for industry.

1 Unit can be represented by 1000 Rs.
0 Unit : stock is under watch but there is no plan to acquire it right now.

Industry name,  Company, Space, Company name (First), Company name (Second), Company name (Third)
Space,          Details, Industry Details,
Space,          Units, <cummuulative units>, Unit (First), Unit (Second), Unit (Third)


NOTE: Try to use just first two words for the company name if that will make it unique in BSE 500.

Fix any discrepancy by running following

 $ cd src/plan
 
 $ ./plan_invoke.sh

Review the generated reports/plan-reports/\*.csv

# DEMAT DATA

Download demat data from ICICI Direct (all holdings, all txns in csv format) in data/demat-data/demat-data.csv 

Fix any discrepancy by running following

 $ cd src/demat
 
 $ ./demat_invoke.sh
 
 Review the generated reports/demat-reports/\*.csv files
 
 # SCREENER Data
 
 Create a watchlist of companies (from plan data) with interesting columns.
 
 Download the screener data in data/screener-data/\*.csv
 
 Generate screener reports using
 
 $ cd src/screener
 
 $ ./screener_invoke.sh
 
 Review the generated reports/screener-reports/\*.csv files
 
 NOTE: To be switched to Quandl or something similar.

 # BONUS share Data (To be modified for new framework)
 # SPLITS share data (to be coded)
 # DIVIDEND Data (To be modified)

 # TBD Data (To Be Done)
  
To know units to be acquired in this quarter (with 6 month delay : 2 Quarter delay)

Execute following

   $ cd src/tbd
   
   $ ./tbd-invoke.sh

Review the generated files reports/tbd-reports/\*.csv

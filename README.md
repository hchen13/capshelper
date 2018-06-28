# CAPS Helper (still in development)

This project acts as a helper module which aims at preparing cryptocurrency data used for the other project called "[CAPS](https://github.com/hchen13/caps.git)" in neural network training and predicting. 

## Project Structure

THe project has 2 sub-modules: **downloader** and **butler**, and several scripts to run various tasks, such as starting a program to continuously download data and save to the database.

### DOWNLOADER

This sub-module performs data downloading from multiple backends, including [CCCAGG](https://www.cryptocompare.com), [Huobi.pro](https://huobi.pro) (planned, yet to implement) and more. Note that the downloader currently only focuses on **hourly** candlestick data.

#### Usage

The module provides a user interface class ```Downloader```, all the APIs are enclosed in the methods of the class.

```Python
downloader = Downloader()

# these are the UNIX timestamps indicating the time period at which we would like to 
# retrieve the candlesticks data
start_timestamp = datetime(2018, 1, 1, 0, 0).timestamp()
end_timestamp = datetime(2018, 6, 1, 23, 59).timestamp()

# the following snippet requests the web data provider the btc/usdt pair candlesticks data 
# from 1/1/2018 00:00 to 6/1/2018 23:59
candlesticks = downloader.get_candlesticks('btc', 'usdt', start=start_timestamp, end=end_timestamp)
```

### BUTLER

The module manages the database that stores candlesticks data, it also provides a user interface class ```Butler```. Data downloaded using ```Downloader``` module can be fed into ```Butler``` for saving into database. Or retrieving candlesticks from the database. Plase note that the Butler **only supports MySQL** database system. 

Another important role the Bulter plays is data pre-processing. The candlesticks data downloaded from CCCAGG or huobi.pro consists only open, close, high, low prices and volume for a coin pair at a timestamp, which is insufficient for technical analysis. The butler derives several extra indicators from it, which are:

1. **SMA 6**: the 6-hour period simple moving averages
2. **SMA 12**: the 12-hour period simple moving averages
3. **SMA 24**: the 24-hour simple moving averages
4. **MACD**: the typical moving averages convergence & divergence indicators, including MACD line, MACD signal, and MACD histogram a.k.a MACD difference.

The followings are the functions implemented and utilized in the module which generates the above indicators

#### SMA function

Given a series of numbers $a=\{a_1, a_2, a_3, ...\}$, the SMA $n$ stands for the average of the latest $n$ values. Therefore, function $SMA(i;n)$ denotes the moving average value at index $i$ with a average window size of $n$. 
$$
    SMA(i;n) = { \sum_{k=0}^{n-1} a_{i-k}  \over n}
$$

#### EMA function

Given a series of numbers $a=\{a_1, a_2, a_3, ...\}$, the EMA $n$ stands for the exponential average of the latest $n$ values. Definitions as follow

$$
    EMA(i;n) = \beta EMA(i-1;n) + (1 - \beta) a_i
$$
where $\beta=1-{2\over {n+1}}$ and $EMA(1;n)=a_1$

#### MACD function

Given a series of numbers $a=\{a_1, a_2, a_3, ...\}$, the MACD is composed of 3 indicators: the MACD line, MACD signal, and MACD histogram, and the definition is

$line(i) = EMA(i; 12|a) - EMA(i; 26|a)$

$signal(i) = EMA(i; 9|line)$

$histogram = line - signal$

#### Usage

0. instantiate butler object:

```Python
butler = Butler(db_configs={
    'host': '<database_location>',
    'name': '<database_schema_name>',
    'user': '<database_username>',
    'pwd': '<password>'
})
```
1. retrive candlesticks data
```Python
begin = datetime(2018, 1, 1, 0, 0).timestamp()
end = datetime(2018, 6, 25, 23, 59).timestamp()
candlesticks = butler.retrieve_candlesticks('btc', 'usdt', start=begin, end=end)
```
2. save candlesticks data into database
```Python
candlesticks = downloader.get_candlesticks('btc', 'usdt', start=start_timestamp, end=end_timestamp)

# the method returns an integer indicating how many of the candlesticks are actually saved as rows in the database
added = butler.save_candlesticks(candlesticks)
```
3. update candlesticks with calculated indicators
```Python
butler.update_indicators('btc', 'usdt')
```

### Scripts

The [app.py](./listener.py) script contains several tasks enclosed in the functions. 

#### get_watchlist

This function produces a list of coins we are interested in and wanting to keep track of. When the keyword argument `from_cache=True`, the function reads directly from the cached [json file](./watchlist.json) located in the project root directory; when it's set to `False`, the function asks the server the most "popular" coins traded across all the exchanges and saves the most recent responses in the same cache json file while returning the same response back. 

#### single_run

This function runs a single pass of the process in which the program downloads and saves the most recent candlesticks data of all the coins in the watchlist countered with the 3 most popular OTC coins (BTC, USDT, and ETH), then updates the new entries with extra indicators, such as SMA 6, MACD, etc.


# Pycryptotradebot
The Python Crypto Currency Tradebot issues buy and sell API requests to
supported crypto currency exchange. This is useful for simulating simple trade
strategies.

___
### IMPORTANT
- This Software is for educational purposes only and does not constitute
investment advice. There is no liability for any monetary gains or losses, or any
other expenses, damages, or losses incurred using this Software. 

- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

- Full license text for this software is in the [LICENSE.txt](LICENSE.txt) file.
- Any purchases using this software imply you are prepared to sustain a total loss of the money you have invested plus any commission or other transaction charges. 
- We recommend keeping the default setting of `safemode: True` and not populating API credentials. 
___

### Tradebot stages
By default the Tradebot uses a simple 4 stage strategy:
 1. **prebuy** - monitor for a certain drop in value
 2. **trailing_buy** - issue a buy order using trailing stop buy strategy 
 3. **presell** - monitor for a certain rise in value 
 4. **trailing_sell** - issue a sell order using trailing stop sell strategy

### Features
- Automatically execute a buy and sell strategy
- Execute buy or sell only 
- Limit buy and sells
- Trailing buy and sells

## Getting Started
1. Instantiate the long running ticker Database process against an exchange and
product offered on that exchange:
`python tickerdb.py gemini BTCUSD`
2. Instantiate a bot using command: `python tradebot.py mybot`

### Prerequisites
1. python 2 interpreter
2. In case you want to execute actual trades, an Exchange Account and API
credentials are required.

### Installing

1. **Install Python:** Ensure the Python interpreter on your computer. This is the program that
  reads Python programs and carries out their instructions. Mac OSX
  distributions from 10.3 (Panther) and up include a version of Python. Linux
  distributions also frequently include Python, which is readily
  upgraded. Please see the python guide if your platform does not already
  include python.

2. **Download Tradebot:** Download the Tradebot git repo

3. **Start long running ticker process:** This is a long running process that
gathers cryptocurrency value data points every minute. Before a Tradebot can
be started, the ticker process for corresonding exchange and symbol must be started 

```
python tickerdb.py <exchange> <symbol>
```

For example, the following command will start gathering data points for BTC
value in USD from the Gemini Exchange:

```
python tickerdb.py gemini BTCUSD
```

 - **exchange:** The Exchange to run this bot against. Currently supported
  exchanges are: `gdax` or `gemini`

 - **symbol:** Symbol representing crypto currency and base currency pair.
   - [GDAX](https://api.gdax.com/products) examples include: BTC-USD, LTC-USD, ETH-USD
   - [Gemini](https://api.gemini.com/v1/symbols) examples include: BTCUSD, ETHUSD


## Running a Trade bot

- Edit `config.yml` file to define one or more bots. 

- Use the following command to instantiate the a bot named `mybot`:
`python tradebot.py mybot`

- Monitor the bot behavior by inspecting its output. Output will be refreshed
  based on 'default_interval' parameter.

## Bot Definition:

The parameters below are used to define a bot. The following section has examples.

- **bot_name:** Name of the bot. When using botmanager, the name should be
unique. E.g: `mybot`. _Required_.
 - **exchange:** The Exchange to run this bot against. Currently supported
  exchanges are: `gdax` or `gemini`. _Required_.

 - **mode:** Actions this bot will perform, acceptable values are `auto`, `buy` and `sell`
   - `mode:auto` will execute buy and sell
   - `mode:buy` will execute buy(s) only
   - `mode:sell` will execute sell(s) only

 - **sym:** Symbol representing crypto currency and base currency pair. _Required_
   - [GDAX](https://api.gdax.com/products) examples include: BTC-USD, LTC-USD, ETH-USD
   - [Gemini](https://api.gemini.com/v1/symbols) examples include: BTCUSD, ETHUSD

 - **base_unit:** Amount of base currency such as USD or EUR, part of the
   `sym` parameter. This amount of crypto currency will be bought or sold. _Required_.

 - **base_value:** Value to compare against when buying. Can be `daily_avg`,
   `weekly_avg`, `hourly_avg` or a static value (e.g. `15000`). Currently only
   Simple Moving Average (SMA) is supported. _Required_. A static base_value can only be used when `mode:buy` or `mode:sell`. 

 - **buy_delta_percent:** Delta between `base_value` and current value at which
 to trigger a buy. E.g. 7.5%. _Required_ for `mode:auto` and `mode:buy`.

 - **sell_delta_percent:** Delta between buy value and current value at which
 to trigger a sell. E.g. 15%. _Required_ for `mode:auto` and `mode:sell`.

 - **trailing_percent:** Percent for trailing stop sell and buys. Set this to
 zero to disable trailing stop mode and issue buy or sell
 immediately. _Required_.

 - **default_interval:** Checks current value every
 interval seconds. _Optional_: Default is 60 seconds.

 - **trailing_interval:** Checks current value every interval seconds during
 trailing_sell or trailing_buy modes. _Optional_: Default is 10 seconds.

 - **prev_purchase_val:** In case of sell mode this sets the purchase value to
 compare `sell_delta_percent` against. _Required_ when `mode:sell`. 

 - **iterations_to_live:** # of cycles this bot should execute before exitting
 _Optional_. Default is 3.

### Advanced settings

Populating the following settings will cause actual buy and sell commands to
be issued.

___
### IMPORTANT
- This Software is for educational purposes only and does not constitute
investment advice. There is no liability for any monetary gains or losses, or any
other expenses, damages, or losses incurred using this Software. 

- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

- Full license text for this software is in the [LICENSE.txt](LICENSE.txt) file.
- Any purchases using this software imply you are prepared to sustain a total loss of the money you have invested plus any commission or other transaction charges. 
- We recommend keeping the default setting of `safemode: True` and not populating API credentials. 
___


- **api_key:** API key without quotes. _Optional_ missing parameter will force `safemode:True`

- **api_secret:** API secret without quotes. _Optional_ missing parameter will force `safemode:True`

- **passphrase:** GDAX also needs a passphrase. _Optional_ missing parameter will force `safemode:True`, only needed for gdax API

- **safemode:** True or False. _Optional_: Default is True.

  - `safemode:True` will NOT issue actual buy / sell commands to exchange. This
 is recommended for getting started and testing trade strategies.

  - `safemode:False` Will issue actual buy / sell commands to exchange. This
 setting is for advanced users as there is a risk of loss.


## Bot examples
Below are a few bot examples

### Example 1
This bot will trigger a trailing buy on Gemini for $50 worth of BTC once the current value reaches 7.5% below daily average. It will trigger a trailing sell once the current value reaches 15% above buy price. This bot will trigger continue to perform buy and sells until stopped. 
```
mybot1:
    exchange: gemini
    sym: BTCUSD
    base_unit: 50
    base_value: daily_avg
    buy_delta_percent: 7.5
    sell_delta_percent: 15
    trailing_percent: 1
    mode: auto
```

### Example 2
This bot will trigger a trailing sell on GDAX for $50 worth of BTC once the current value reached 20% above a previous buy price of: $12,800
```
mybot2:
    exchange: gdax
    sym: BTCUSD
    dryrun: False
    unitusd: 100
    base_value: daily_avg
    buy_delta_percent: 10
    sell_delta_percent: 20
    trailing_percent: 1
    mode: sell
    prev_purchase_val: 12800
```

## Bot deployment
The Tradebot can be deployed in local or server environments. 

### Local Deployment

Use `tradebot.py` to run in a local environment. The following command will instantiate a bot named `bot1` defined in `config.yml`:

`python tradebot.py bot1`

### Server Deployment

Use `tradebotmanager.py` to run in a server environment and instantiate multiple bots. The following command will instantiate all bots defined in `config.yml`. Note: any previously run bot names will be skipped, therefore ensure your bot names are new / unique.

`python tradebotmanager.py config.yml`

In a server deployment bots will automatically redirect their outputs into a  `bot_name.out.txt` file in the `logs/` directory.

### Stopping a bot

Bots will monitor the deployment directory for a file called `bot_name.stop` and stop after at the defined interval.

For example, to stop `bot1`, create a file in the deployment directory called `bot1.stop`. It Mac or Linux this can be done using the command below:

`touch bot1.stop`


## Built With

* [Python](https://docs.python.org/) - Python
* [Gemini](https://docs.gemini.com/rest-api/) - Gemini REST API
* [Gdax](https://docs.gdax.com/#api) - GDAX REST API

## Contributing

## Versioning
* **V1** - *First release* - Includes support for GDAX and Gemini exchanges,
Simple Moving Average, auto, buy and sell modes.

## Authors

* **Kawsar** - *Initial work* - [kawsark](https://gitlab.com/kawsark/)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

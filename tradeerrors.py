class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        parameter -- the parameter for which we received an invalid argument
    """

    def __str__(self):
        return "Invalid input: %s for parameter: %s" % (self.expression,self.parameter)

    def __init__(self, expression, parameter):
        self.expression = expression
        self.parameter = parameter

class InsufficientFundsError(Error):
    """Raised when a buy or sell operation is attempted and there are not enough funds in the account

    Attributes:
        availablefunds -- balance available to trade
        qty -- qty attemtpted to buy or sell
    """

    def __str__(self):
        return "Not enough funds available for this operation. Requested qty: %f, available to trade: %f" % (self.qty,self.availablefunds)

    def __init__(self, availablefunds, qty):
        self.availablefunds = availablefunds
        self.qty = qty

class OrderPlacementError(Error):
    """Raised when a buy or sell operation is attempted and there is an error returned by the Exchange

    Attributes:
        responsetxt -- response returned by Exchange
    """

    def __str__(self):
        return "OrderPlacementError, received response from Exchange:" + self.responsetxt

    def __init__(self, responsetxt):
        self.responsetxt = responsetxt

class UnknownResponseError(Error):
    """Raised when a buy or sell operation is attempted and there is an unexpected response by the Exchange

    Attributes:
        responsetxt -- response returned by Exchange
    """

    def __str__(self):
        return "UnknownResponseError, received response from Exchange:" + self.responsetxt

    def __init__(self, responsetxt):
        self.responsetxt = responsetxt

class BotIniterror(Error):
    """Raised when there is an initialization error when starting a Bot

    Attributes:
        message -- details of the initialization error
    """

    def __str__(self):
        return "BotIniterror, received error while initializing:" + self.message

    def __init__(self, message):
        self.message = message
        
        

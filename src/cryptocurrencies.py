# coding: utf8

"""
All Cryptocurrency Constants
"""
from data_collection import Cryptocurrency


ETHEREUM = Cryptocurrency("Ethereum", "ETH")
RIPPLE = Cryptocurrency("Ripple", "XRP")
EOS = Cryptocurrency("Eos", "EOS")
CARDANO = Cryptocurrency("Cardano", "ADA")
NEO = Cryptocurrency("Neo", "NEO")
VECHAIN = Cryptocurrency("Vechain", "VET")
ONTOLOGY = Cryptocurrency("Ontology", "ONT")
DECRED = Cryptocurrency("Decred", "DCR")
NANO = Cryptocurrency("Nano", "NANO")
ICON = Cryptocurrency("Icon", "ICX")

CRYPTOS = (ETHEREUM, RIPPLE, EOS, CARDANO, NEO,
        VECHAIN, ONTOLOGY, DECRED, NANO, ICON)


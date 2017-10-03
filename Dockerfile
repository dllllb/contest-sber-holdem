FROM sberbank/python

ADD winrate /winrate

RUN pip install -e /winrate

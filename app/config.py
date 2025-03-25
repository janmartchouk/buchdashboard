# config.py

# Dictionary of websites for buying books. The keys are the names of the sites,
# and the values are the URL templates where {isbn} will be replaced by the actual ISBN.
BUYING_SITES = {
        'booklooker': 'https://www.booklooker.de/B%C3%BCcher/Angebote/isbn={isbn}?sortOrder=preis_total',
        'zvab': 'https://www.zvab.com/servlet/SearchResults?ch_sort=t&cm_sp=sort-_-SRP-_-Results&ds=30&isbn={isbn}&rollup=on&sortby=2',
        'medimops': 'https://www.medimops.de/produkte-C0/?fcIsSearch=1&searchparam={isbn}&listorder=asc&listorderby=oxvarminprice',
        'rebuy': 'https://www.rebuy.de/kaufen/suchen?q={isbn}&sortBy=price_asc&inStock=1',
        'bookbot': 'https://bookbot.de/p/instock/1/language/4/q/{isbn}.price_asc',
        'abebooks': 'https://www.abebooks.de/servlet/SearchResults?ch_sort=t&cm_sp=sort-_-SRP-_-Results&ds=20&kn={isbn}&rollup=on&sortby=2',
        'eurobuch': 'https://www.eurobuch.de/buch/isbn/{isbn}.html',
        'buchfreund': 'https://www.buchfreund.de/de/angebote/{isbn}/'
#        'ebay': "https://www.ebay.de/sch/i.html?_nkw={isbn}&_sacat=0&_from=R40&_sop=15"
}


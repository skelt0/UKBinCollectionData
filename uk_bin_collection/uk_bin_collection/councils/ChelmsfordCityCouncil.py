import re
import requests
from bs4 import BeautifulSoup

from uk_bin_collection.uk_bin_collection.common import *
from uk_bin_collection.uk_bin_collection.get_bin_data import \
    AbstractGetBinDataClass


# import the wonderful Beautiful Soup and the URL grabber
class CouncilClass(AbstractGetBinDataClass):
    """
    Concrete classes have to implement all abstract operations of the
    base class. They can also override some operations with a default
    implementation.
    """

    def parse_data(self, page: str, **kwargs) -> dict:
        data = {"bins": []}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"}

        # Make a BS4 object
        soup = BeautifulSoup(page.text, features="html.parser")
        soup.prettify()

        # Get collection calendar
        calendar_urls = soup.find_all("a", string=re.compile(r"view or download the collection calendar"))
        if len(calendar_urls) > 0:
            requests.packages.urllib3.disable_warnings()
            response = requests.get(calendar_urls[0].get("href"), headers=headers)

            # Make a BS4 object
            soup = BeautifulSoup(response.text, features="html.parser")
            soup.prettify()

            # Loop the months
            for month in soup.find_all("div", {"class": "usercontent"}):
                year = ""
                if month.find("h2") and 'calendar' not in month.find("h2").get_text(strip=True):
                    year = datetime.strptime(month.find("h2").get_text(strip=True), "%B %Y").strftime("%Y")
                elif month.find("h3"):
                    year = datetime.strptime(month.find("h3").get_text(strip=True), "%B %Y").strftime("%Y")
                if year != "":
                    for row in month.find_all("li"):
                        results = re.search(
                            "([A-Za-z]+ \\d\\d? [A-Za-z]+): (.+)", row.get_text(strip=True)
                        )
                        if results:
                            dict_data = {
                                "type": results.groups()[1].capitalize(),
                                "collectionDate": datetime.strptime(
                                    results.groups()[0] + " " + year, "%A %d %B %Y"
                                ).strftime(date_format),
                            }
                            data["bins"].append(dict_data)

            # Sort collections
            data["bins"].sort(
                key=lambda x: datetime.strptime(x.get("collectionDate"), "%d/%m/%Y")
            )

        return data

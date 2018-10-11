# coding: utf-8
import requests
from bs4 import BeautifulSoup

website_prefix = "https://www.reuters.com/"
search_prefix = "https://www.reuters.com/finance/stocks/lookup?searchType=any&search="


def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        html_doc =  request_result.text
        soup = BeautifulSoup(html_doc,"html.parser")
        return soup

def _convert_string_to_float(string):
    to_replace = ",()$€%"
    for c in to_replace:
        string = string.replace(c, "")
    return float(string.strip())

def get_url(company):
    res = requests.get(search_prefix + company)
    soup = _handle_request_result_and_build_soup(res)
    links = soup.find("table", class_="search-table-data").find("tr", class_="stripe").attrs['onclick'].replace("parent.location=", "").strip("'")

    url = website_prefix + links
    url = url.replace("overview", "financial-highlights")

    return url

def get_results_for_company(company):

    results_dict = {}

    url = get_url(company)
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    table = soup.find_all("table", class_= "dataTable")

    # les ventes au quartier à fin décembre 2018
    ventes_au_quartier = table[0].find_all("td", class_="data")[1].text
    results_dict["Ventes au quartier"] = _convert_string_to_float(ventes_au_quartier)

    # le prix de l'action et son % de changement au moment du crawling
    prix_action = soup.find_all("div", class_= "sectionQuote nasdaqChange")[0].find_all("span")[1].text
    results_dict["Prix de l'action"] = _convert_string_to_float(prix_action)

    taux_de_changement = (
        soup.find_all("div", class_= "sectionQuote priceChange")[0]
        .find_all("span", class_="valueContentPercent")[0]
        .text

    )
    results_dict["% de changement"] = _convert_string_to_float(taux_de_changement)


    # le % Shares Owned des investisseurs institutionels
    shares_owned = table[-1].find_all("td", class_="data")[0].text
    results_dict["% Shares Owned"] = _convert_string_to_float(shares_owned)

    # le dividend yield de la company, le secteur et de l'industrie
    dividend_yield = table[2].find_all("td", class_="data")[:3]
    results_dict["divident_yield"] = {
        "company": _convert_string_to_float(dividend_yield[0].text),
        "industry": _convert_string_to_float(dividend_yield[1].text),
        "sector": _convert_string_to_float(dividend_yield[2].text)
    }

    return results_dict

print("LVMH: ", get_results_for_company("LVMH"))
print()
print("Airbus: ", get_results_for_company("Airbus"))
print()
print("Danone:", get_results_for_company("Danone"))

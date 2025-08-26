import requests
import pandas
import textstat
from bs4 import BeautifulSoup

class Knjige:

    def __init__(self, naslov, avtor, link):
        self.naslov = naslov
        self.avtor = avtor
        self.link = link
        self.izid = "N/A"
        self.ocena = "N/A"
        self.zanr = "N/A"

    
knjige = []

def pridobitev_podatkov1():
    for page in range(20):

        url = f"https://www.gutenberg.org/ebooks/bookshelf/{page}"
        soup = BeautifulSoup(requests.get(url).text, "html.parser")

        try:
            for li in soup.select("li.booklink"):
                title = li.select_one(".title").text.strip()
                author = li.select_one(".subtitle").text.strip()
                link = "https://www.gutenberg.org" + li.a["href"]

                knjige.append(Knjige(title, author, link))

        except Exception:
            print (Exception)

podatki = []
def pridobitev_podatkov2():
    urls = [(knjiga.link, knjiga.naslov) for knjiga in knjige]
    i=0
    for url, naslov in urls:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, "html.parser")

        release_tag = soup.find(string="Release Date")
        release_date = release_tag.find_next().get_text(strip=True) if release_tag else "Unknown"

        lang_tag = soup.find(string="Language")
        language = lang_tag.find_next().get_text(strip=True) if lang_tag else "Unknown"

        # Poiščemo plain text link
        link_tag = soup.find("a", string="Plain Text UTF-8")
        if link_tag and "href" in link_tag.attrs:
            text_url = "https:" + link_tag["href"] if link_tag["href"].startswith("//") else "https://www.gutenberg.org" + link_tag["href"]
            text_resp = requests.get(text_url)
            book_text = text_resp.text[:10000]  # analiziramo le prvih 10.000 znakov, da je hitreje
        
            # Reading ease score
            flesch_score = textstat.flesch_reading_ease(book_text)
            grade = textstat.text_standard(book_text, float_output=False)

            if flesch_score >= 80:
                comment = "Very easy to read."
            elif flesch_score >= 70:
                comment = "Fairly easy to read."
            elif flesch_score >= 60:
                comment = "Plain English. Easily understood."
            elif flesch_score >= 50:
                comment = "Fairly difficult to read."
            else:
                comment = "Difficult to read."

        else:
            reading_level = "Unknown"

        dl_tag = soup.find(string="Downloads")
        downloads = dl_tag.find_next().get_text(strip=True) if dl_tag else "Unknown"
        downloads = downloads[:-31]

        podatki.append({
            "title": naslov, 
            "url": url,
            "author": knjige[i].avtor,
            "release_date": release_date,
            "language": language,
            "reading_level": comment,
            "downloads_last_30d": downloads
        })
        i+=1

        df = pandas.DataFrame(podatki)
        df.to_csv("gutenberg_books.csv", index=False, encoding="utf-8")
        print(df)



pridobitev_podatkov1()
pridobitev_podatkov2()
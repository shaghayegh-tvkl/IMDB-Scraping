from TextRank import TextRank4Keyword
from bs4 import BeautifulSoup
from requests import get
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from csv import writer

url1 = "https://www.imdb.com/list/ls097968074/"


class IMDB(object):
    def __init__(self, url):
        super(IMDB, self).__init__()
        page = get(url)
        self.soup = BeautifulSoup(page.content, 'lxml')

    def articleTitle(self):
        return self.soup.find("h1", class_="header").text.replace("\n", "")

    def bodyContent(self):
        content = self.soup.find(id="main")
        return content.find_all("div", class_="lister-item mode-detail")

    def movieData(self):
        movieFrame = self.bodyContent()
        movieTitle = []
        movieLink = []
        movieDescription = []
        keyword = []

        tr4w = TextRank4Keyword()
        for movie in movieFrame:
            movieFirstLine = movie.find("h3", class_="lister-item-header")

            movieTitle.append(movieFirstLine.find("a").text)
            link = movieFirstLine.find('a')["href"]
            movieLink.append("http://imdb.com" + link)

            desc = movie.find_all("p", class_="")[-1].text.lstrip()
            movieDescription.append(desc)
            tr4w.analyze(desc, candidate_pos=[
                'NOUN', 'PROPN'], window_size=4, lower=False)
            keyword.append(str(tr4w.get_keywords(10)))

        movieData = [movieTitle, movieDescription, movieLink, keyword]
        return movieData


id1 = IMDB(url1)

movieData = id1.movieData()


# for i in range(len(movieData[0])):
#     print("Title: " + movieData[0][i])
#     print("Description: " + movieData[1][i])
#     print("Link: " + movieData[2][i])
#     print("Keyword: " + movieData[3][i])

#     print("----------------------------------------------------------------------------------------")


G = nx.Graph()

with open('./docs/nodes.csv', 'a') as f_object:
    writer_object = writer(f_object)
    for i in range(len(movieData[0])):
        for j in range(len(movieData[0])):
            if(movieData[0][i] != movieData[0][j]):
                common = set(eval(movieData[3][i])).intersection(set(eval(movieData[3][j])))
                if(len(common) != 0):
                    # print(movieData[0][i] + " - " + movieData[0][j])
                    # print(len(common))
                    writer_object.writerow([movieData[0][i],movieData[0][j],len(common)])

                    G.add_edge(movieData[0][i], movieData[0][j], weight=len(common))

    f_object.close()


pos = nx.spring_layout(G, k=0.3*1/np.sqrt(len(G.nodes())), iterations=20)
plt.figure(3, figsize=(30, 30))
nx.draw(G, pos=pos)
nx.draw_networkx_labels(G, pos=pos)
plt.savefig("./docs/imdb-movies.png")
plt.show()

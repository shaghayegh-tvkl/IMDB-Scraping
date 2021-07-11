from TextRank import TextRank4Keyword
from bs4 import BeautifulSoup
from requests import get
import matplotlib.pyplot as plot
import networkx
import numpy
from csv import writer

IMDB_URL = "https://www.imdb.com/list/ls097968074/"


class IMDB(object):
    def __init__(self, url):
        super(IMDB, self).__init__()
        page = get(url)
        self.soup = BeautifulSoup(page.content, 'lxml')

    def body_content(self):
        content = self.soup.find(id="main")
        return content.find_all("div", class_="lister-item mode-detail")

    def movie_data(self):
        movie_frame = self.body_content()
        movie_title = []
        movie_link = []
        movie_description = []
        keyword = []

        tr4w = TextRank4Keyword()
        for movie in movie_frame:
            movie_header = movie.find("h3", class_="lister-item-header")

            movie_title.append(movie_header.find("a").text)
            link = movie_header.find('a')["href"]
            movie_link.append("http://imdb.com" + link)

            description = movie.find_all("p", class_="")[-1].text.lstrip()
            movie_description.append(description)
            tr4w.analyze(description, candidate_pos=[
                'NOUN', 'PROPN'], window_size=4, lower=False)
            keyword.append(str(tr4w.get_keywords(10)))

        movie_data = [movie_title, movie_description, movie_link, keyword]
        return movie_data


obj = IMDB(IMDB_URL)

movie_data = obj.movie_data()


for i in range(len(movie_data[0])):
    print("Title: " + movie_data[0][i])
    print("Description: " + movie_data[1][i])
    print("Link: " + movie_data[2][i])
    print("Keyword: " + movie_data[3][i])

    print("----------------------------------------------------------------------------------------")


Movie_Graph = networkx.Graph()

with open('./docs/nodes.csv', 'a') as file_object:
    writer_object = writer(file_object)
    for i in range(len(movie_data[0])):
        for j in range(len(movie_data[0])):
            if(movie_data[0][i] != movie_data[0][j]):
                common = set(eval(movie_data[3][i])).intersection(set(eval(movie_data[3][j])))
                if(len(common) != 0):
                    writer_object.writerow([movie_data[0][i],movie_data[0][j],len(common)])

                    Movie_Graph.add_edge(movie_data[0][i], movie_data[0][j], weight=len(common))

    file_object.close()


pos = networkx.spring_layout(Movie_Graph, k=0.3*1/numpy.sqrt(len(Movie_Graph.nodes())), iterations=20)
plot.figure(3, figsize=(30, 30))
networkx.draw(Movie_Graph, pos=pos)
networkx.draw_networkx_labels(Movie_Graph, pos=pos)
plot.savefig("./docs/imdb-movies.png")
plot.show()

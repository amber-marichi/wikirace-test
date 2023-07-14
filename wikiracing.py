from collections import deque
from typing import List

import psycopg2
import requests
from requests import Response
from bs4 import BeautifulSoup
from ratelimiter import RateLimiter
from urllib.parse import unquote

import queries


# requests configs
requests_per_minute = 100
links_per_page = 200
time_period = 60
MAIN_URL = "https://uk.wikipedia.org/wiki/"


# db configs
POSTGRES_HOST = "localhost"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_DB = "postgres"
POSTGRES_DB_PORT = 5432


@RateLimiter(max_calls=requests_per_minute, period=time_period)
def get_page(page_name: str) -> Response:
    url = MAIN_URL + page_name

    try:
        return requests.get(url)
    except requests.exceptions.HTTPError as err:
        print(err)


class WikiDataBase:
    def __init__(self) -> None:
        self.connection = psycopg2.connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_DB_PORT,
        )
        self.cursor = self.connection.cursor()
        self._check_create_tables()

    def __del__(self) -> None:
        self.cursor.close()
        self.connection.close()

    def _check_create_tables(self) -> None:
        self.cursor.execute(queries.CREATE_ARTICLE_TABLE)
        self.cursor.execute(queries.CREATE_LINK_TABLE)

    def get_article_id(self, article_name: str) -> int:
        self.cursor.execute(queries.ADD_ARTICLE_QUERY, (article_name,))
        self.connection.commit()

        self.cursor.execute(queries.GET_ARTICLE_QUERY, (article_name,))

        return self.cursor.fetchone()[0]

    def get_links_from_db(self, article_id: int) -> List[str]:
        self.cursor.execute(queries.GET_LINKS_QUERY, (article_id,))
        result = self.cursor.fetchall()

        return [val[0] for val in result]

    def add_links(self, article_id: int, link_list: List[str]) -> None:
        link_id_list = [self.get_article_id(link) for link in link_list]
        values = [(article_id, link_id) for link_id in link_id_list]
        self.cursor.executemany(queries.ADD_LINKS_QUERY, values)
        self.connection.commit()


class WikiRacer:
    def __init__(self) -> None:
        self.database = WikiDataBase()

    @staticmethod
    def _get_links_from_page(article_name: str) -> List[str]:
        page_content = get_page(article_name)
        soup = BeautifulSoup(page_content.text, "html.parser")
        all_link_found = soup.findAll("a")

        link_list = []
        link_count = 0
        for link in all_link_found:
            temp_link = link.get("href")
            if temp_link and temp_link.startswith("/wiki/") and ":" not in temp_link:
                link_count += 1
                if link_count == links_per_page:
                    break
                link_list.append(unquote(temp_link)[6:].replace("_", " "))

        return link_list

    def _get_all_links(self, article_name: str) -> List[str]:
        article_id = self.database.get_article_id(article_name)
        link_list = self.database.get_links_from_db(article_id)
        if link_list:
            return link_list

        link_list = self._get_links_from_page(article_name)
        self.database.add_links(article_id, link_list)

        return link_list

    def find_path(self, start: str, finish: str) -> List[str]:
        queue = deque([[start]])
        seen = set()

        while queue:
            cur_path = queue.popleft()
            cur_article = cur_path[-1]

            if cur_article in seen:
                continue

            seen.add(cur_article)
            article_links = self._get_all_links(cur_article)

            for link in article_links:
                edited_path = cur_path + [link]
                if link == finish:
                    return edited_path
                queue.append(edited_path)


if __name__ == "__main__":
    racer = WikiRacer()
    path = racer.find_path("Дружба", "Рим")
    print(path)

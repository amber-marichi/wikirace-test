CREATE_ARTICLE_TABLE = (
  "CREATE TABLE IF NOT EXISTS articles ("
  "id SERIAL PRIMARY KEY, "
  "title VARCHAR(255) UNIQUE NOT NULL);"
)


CREATE_LINK_TABLE = (
  "CREATE TABLE IF NOT EXISTS links ("
  "id SERIAL PRIMARY KEY, "
  "from_article INTEGER, "
  "to_article INTEGER, "
  "CONSTRAINT fk_from_article FOREIGN KEY (from_article) REFERENCES articles (id), "
  "CONSTRAINT fk_to_article FOREIGN KEY (to_article) REFERENCES articles (id), "
  "CONSTRAINT uc_connections UNIQUE (from_article, to_article));"
)


GET_ARTICLE_QUERY = "SELECT id FROM articles WHERE title = %s"


ADD_ARTICLE_QUERY = (
  "INSERT INTO articles (title) "
  "VALUES (%s) "
  "ON CONFLICT (title) DO NOTHING;"
)


GET_LINKS_QUERY = (
  "SELECT title "
  "FROM links JOIN articles ON links.to_article=articles.id "
  "WHERE from_article = %s"
)


ADD_LINKS_QUERY = (
  "INSERT INTO links (from_article, to_article) "
  "VALUES (%s, %s) ON CONFLICT DO NOTHING;"   
)

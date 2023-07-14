-- CREATE_ARTICLE_TABLE
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY, 
    title VARCHAR(255) UNIQUE NOT NULL
);


-- CREATE_LINK_TABLE
CREATE TABLE IF NOT EXISTS links (
    id SERIAL PRIMARY KEY, 
    from_article INTEGER, 
    to_article INTEGER, 
    CONSTRAINT fk_from_article FOREIGN KEY (from_article) REFERENCES articles (id), 
    CONSTRAINT fk_to_article FOREIGN KEY (to_article) REFERENCES articles (id), 
    CONSTRAINT uc_connections UNIQUE (from_article, to_article)
);


-- GET_ARTICLE_QUERY
SELECT id FROM articles WHERE title = title_name;


-- ADD_ARTICLE_QUERY
INSERT INTO articles (title) 
VALUES (title_name) 
ON CONFLICT (title) DO NOTHING;


-- GET_LINKS_QUERY
SELECT title 
FROM links JOIN articles ON links.to_article=articles.id 
WHERE from_article = article_id


-- ADD_LINKS_QUERY
INSERT INTO links (from_article, to_article) 
VALUES (from_article_id, to_article_id) ON CONFLICT DO NOTHING;


-- QUERIES TO RUN AFTER DB IS POPULATED

-- TOP 5 ARTICLES WITH BIGGEST NUMBER OF REFERENCES ON IT
SELECT articles.title, COUNT(*) AS connection_count
FROM articles
JOIN links ON articles.id = links.to_article
GROUP BY articles.title
ORDER BY connection_count DESC
LIMIT 5;


-- TOP 5 ARTICLES WITH BIGGEST NUMBER OF REFERENCES ON OTHER
SELECT articles.title, COUNT(*) AS connection_count
FROM articles
JOIN links ON articles.id = links.from_article
GROUP BY articles.title
ORDER BY connection_count DESC
LIMIT 5;


-- GET AVERAGE LINK COUNT FOR ALL LINKS OF GIVEN ARTICLE
SELECT AVG(link_count) AS average_link_count
FROM (
  SELECT (
	  SELECT COUNT(*) FROM links WHERE links.to_article = links.to_article
  ) AS link_count
  FROM links JOIN articles
  ON articles.id=links.from_article
  WHERE title = 'Рим'
) AS subquery;

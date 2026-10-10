def add_article(articles, seen_links, source, title, link, description=""):
    """Add a unique article and track all feeds where it appears."""
    if link not in seen_links:
        seen_links[link] = []

        articles.append({
            "source": source,
            "sources": seen_links[link],
            "title": title,
            "link": link,
            "description": description,
        })

    if source not in seen_links[link]:
        seen_links[link].append(source)

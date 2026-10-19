def add_article(articles, seen_links, source, title, link, description="", content=""):
    """Add a unique article and track all feeds where it appears.

    content is the full article text when the feed provides it; it is used
    only for AI summaries, never for selection (which uses the description).
    """
    if link not in seen_links:
        seen_links[link] = []

        articles.append({
            "source": source,
            "sources": seen_links[link],
            "title": title,
            "link": link,
            "description": description,
            "content": content,
        })

    if source not in seen_links[link]:
        seen_links[link].append(source)

import urllib.parse


def is_valid_url(url):
    if not url or not url.startswith(("https://", "http://")):
        return False

    parsed_url = urllib.parse.urlparse(url)
    return bool(parsed_url.netloc)


def is_duplicate_link(link, seen_links):
    return link in seen_links

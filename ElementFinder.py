def findElement(soup, tagsToText, tagsToAttributes, tags, attributes, texts):
    for t in tags:
        tags = soup.find_all(t)
        
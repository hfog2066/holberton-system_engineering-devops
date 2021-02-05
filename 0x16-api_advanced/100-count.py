#!/usr/bin/python3
"""
defines recursive function to query the Reddit API
to parse title of all hot article and print sorted count
"""


def count_words(subreddit, word_list, after=None, count={}):
    """
    queries the Reddit API
    parses title of all hot articles
    prints sorted count of given keywords
    """
    import json
    import requests
    if after is None:
        sub_URL = 'https://www.reddit.com/r/{}/hot.json'.format(subreddit)
    else:
        sub_URL = 'https://www.reddit.com/r/{}/hot.json?after={}'.format(
            subreddit, after)
    subreddit_info = requests.get(sub_URL,
                                  headers={"user-agent": "user"},
                                  allow_redirects=False)
    for word in word_list:
        word = word.lower()
        if word not in count.keys():
            count[word] = 0
    try:
        data = subreddit_info.json().get("data")
    except:
        return
    children = data.get("children")
    for child in children:
        title = (child.get("data").get("title").lower())
        title = title.split(' ')
        for word in word_list:
            word = word.lower()
            count[word] += title.count(word)
    after = data.get("after")
    if after is None:
        result = []
        for k in count.keys():
            if count[k] != 0:
                if result == []:
                    result.append("{}: {}".format(k, count[k]))
                else:
                    for i in range(len(result)):
                        if count[k] > int(result[i].split(' ')[1]):
                            result = result[:i] + \
                                     ["{}: {}".format(k, count[k])] + \
                                     result[i:]
                            break
                        elif count[k] == int(result[i].split(' ')[1]):
                            alpha_list = [k, result[i].split(' ')[0]]
                            j = 1
                            while count[k] == int(result[i + j].split(' ')[1]):
                                alpha_list.append(result[i + j].split(' ')[0])
                            alpha_list = alpha_list.sort
                            for j in range(len(alpha_list)):
                                if k == alpha_list[j]:
                                    result = result[:i + j] + \
                                             ["{}: {}".format(k, count[k])] + \
                                             result[i + j:]
                        else:
                            continue
                    else:
                        result.append("{}: {}".format(k, count[k]))
        if result != []:
            for printing in result:
                print(printing)
        return
    return (count_words(subreddit, word_list, after, count))

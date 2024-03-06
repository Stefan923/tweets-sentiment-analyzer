import json


def read_json_file(filename):
    with open(filename, 'r') as file:
        data = file.read()
        tweets = [json.loads(tweet.strip().lower()) for tweet in data.split('\n') if tweet.strip()]
        for tweet in tweets:
            tweet['words'] = [word.strip() for word in tweet['text'].split(" ") if word.strip()]
    return tweets


def read_scores_file(filename):
    with open(filename, 'r') as file:
        data = file.read()
        read_data = [obj.split('\t') for obj in data.split('\n')]
        for value in read_data:
            value[1] = int(value[1])
    return read_data


def compute_tweet_score(message, sentiments):
    tweet_score = 0

    for (sentiment, score) in sentiments:
        if sentiment in message:
            tweet_score += score
    return tweet_score


def compute_tweets_scores(tweets, sentiments):
    for tweet in tweets:
        tweet['score'] = compute_tweet_score(tweet['text'], sentiments)
    return tweets


def compute_terms_frequencies(tweets):
    word_frequencies = {}
    for tweet in tweets:
        for word in tweet['words']:
            word_frequencies[word] = word_frequencies.get(word, 0) + 1
    return word_frequencies


def map_apparitions_to_scores(word_scores):
    min_score = min(word_scores.values())
    max_score = max(word_scores.values())
    score_range = max_score - min_score

    new_min = -5
    new_max = 5

    threshold_fraction = 0.05
    threshold = threshold_fraction * score_range

    max_score = min(max_score, threshold)
    min_score = max(min_score, -threshold)

    mapped_scores = {}
    for word, score in word_scores.items():
        if score < 0:
            mapped_score = (max(score, min_score) / min_score) * new_min
        elif score > 0:
            mapped_score = (min(score, max_score) / max_score) * new_max
        else:
            mapped_score = 0
        mapped_scores[word] = int(round(mapped_score))

    return mapped_scores


def compute_score_for_terms(tweets, words, sentiments):
    words_apparitions = {}
    for word, _ in words:
        if word not in sentiments:
            words_apparitions[word] = 0
            for tweet in tweets:
                if word in tweet['words']:
                    if tweet['score'] > 0:
                        words_apparitions[word] = words_apparitions.get(word, 0) + 1
                    elif tweet['score'] < 0:
                        words_apparitions[word] = words_apparitions.get(word, 0) - 1
    return map_apparitions_to_scores(words_apparitions)


def compute_happiness(tweets):
    return sum([tweet['score'] for tweet in tweets]) / len(tweets)


def compare_happiness_by_friends_count(tweets):
    sorted_by_friends = sorted(tweets, key=lambda x: x['user']['friends_count'])

    elements_to_extract = int(len(sorted_by_friends) * 0.3)
    least_friends_tweets = sorted_by_friends[:elements_to_extract]
    most_friends_tweets = sorted_by_friends[-elements_to_extract:]

    least_friends_happiness = compute_happiness(least_friends_tweets)
    most_friends_happiness = compute_happiness(most_friends_tweets)

    if least_friends_happiness > most_friends_happiness:
        print(f"People with less friends (happiness = {least_friends_happiness}) are happier than people with more friends (happiness = {most_friends_happiness}).")
    elif least_friends_happiness < most_friends_happiness:
        print(f"People with less friends (happiness = {least_friends_happiness}) are not happier than people with more friends (happiness = {most_friends_happiness}).")
    else:
        print(f"People with less friends (happiness = {least_friends_happiness}) are as happy as people with more friends (happiness = {most_friends_happiness}).")


if __name__ == '__main__':
    tweets = read_json_file('../resources/twitter_data1.txt')
    sentiment_scores = read_scores_file('../resources/sentiment_scores.txt')

    print("\n1) Tweets sentiment scores:")
    tweets = compute_tweets_scores(tweets, sentiment_scores)
    with open('result_1.txt', 'w', encoding='utf-8') as file:
        for i, tweet in enumerate(tweets, start=1):
            file.write(f"{i}. ('text': {tweet['text']}, 'score': {tweet['score']})\n")
    print("  DONE - results written to result_1.txt")

    print("\n--------------------------------\n\n2) First 500 most frequent terms:")
    sorted_terms_frequencies = sorted(compute_terms_frequencies(tweets).items(), key=lambda x: x[1],
                                      reverse=True)
    most_frequent_terms = sorted_terms_frequencies[:500]
    with open('result_2.txt', 'w', encoding='utf-8') as file:
        for i, (word, frequency) in enumerate(most_frequent_terms, start=1):
            file.write(f"{i}. {word}: {frequency}\n")
    print("  DONE - results written to result_2.txt")

    print("\n--------------------------------\n\n3) Computed scores for most frequent sentiments:")
    most_frequent_terms_scores = compute_score_for_terms(tweets, most_frequent_terms, sentiment_scores)
    with open('result_3.txt', 'w', encoding='utf-8') as file:
        for i, (word, score) in enumerate(most_frequent_terms_scores.items(), start=1):
            file.write(f"{i}. {word}: {score}\n")
    print("  DONE - results written to result_3.txt")

    print("\n--------------------------------\n\n4) Check if people with more friends are happier:")
    compare_happiness_by_friends_count(tweets)

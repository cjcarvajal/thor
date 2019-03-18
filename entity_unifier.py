import twitter_client


def unify_entities_on_tweet(tweet):
    tweet.nee_entities = [unify_entity(entity)
                          for entity in tweet.nee_entities]
    return tweet


def unify_entity(entity):
    if entity.entity_type == 'PERSON' and entity.text.startswith('@'):
        twitter_user = twitter_client.get_user_by_handle(entity.text[1:])
        entity.text = twitter_user[0]['name']
    return entity

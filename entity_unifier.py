import twitter_client


def unify_entities_on_tweet(tweet, persisted_accounts):
    tweet.nee_entities = [unify_entity(entity, persisted_accounts)
                          for entity in tweet.nee_entities]
    return tweet


def unify_entity(entity, persisted_accounts):
    if entity.entity_type == 'PERSON' and entity.text.startswith('@'):
        if entity.text in persisted_accounts:
            entity.text = persisted_accounts[entity.text]
        else:
            try:
                twitter_user = twitter_client.get_user_by_handle(
                    entity.text[1:])
                retrieved_name = twitter_user[0]['name']
                persisted_accounts.update({entity.text: retrieved_name})
                entity.text = retrieved_name

            except Exception as e:
                print(e)
                print('Entity Unifier')
                print(twitter_user)
    return entity

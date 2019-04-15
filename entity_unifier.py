import twitter_client
from unified_entities import falses_entities, false_entities_pattern, final_entities
import re
import unidecode


def unify_entities_on_tweet(tweet, persisted_accounts):
    tweet.nee_entities = [unify_entity(entity, persisted_accounts)
                          for entity in tweet.nee_entities]
    tweet.nee_entities = [
        not_blank_entity for not_blank_entity in tweet.nee_entities if not_blank_entity.text]
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
    else:
        entity.text = unify_text_from_list(entity.text)
    return entity


def unify_text_from_list(entity_text):
    if entity_text in [normalize_text(false) for false in falses_entities]:
        return ''

    for pattern in false_entities_pattern:
        if re.match(pattern.lower(), entity_text.lower()):
            return ''

    possible_unified_list = [
        x for x in final_entities if normalize_text(entity_text) in [normalize_text(nick) for nick in x['nicknames']]]
    if possible_unified_list:
        return possible_unified_list[0]['realname']
    return entity_text


def normalize_text(text):
    return unidecode.unidecode(text).lower()

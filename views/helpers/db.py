import datetime
import hashlib
import logging

from google.cloud import firestore

from settings import DEFAULT_PARAMS


class InvalidCodeError(RuntimeError):
    pass


class UsedCodeError(RuntimeError):
    pass


class InvalidSubIdError(RuntimeError):
    pass


def get_date_group(dt=None):
    if dt is None:
        dt = datetime.datetime.today()
    id = int(dt.toordinal() / 10)
    return f'{id:06d}'


def gen_id(*src):
    str2hash = '-'.join(src)
    result = hashlib.md5(str2hash.encode())
    return result.hexdigest()


def get_client():
    return firestore.Client()


def get_system(client):
    ret = DEFAULT_PARAMS
    doc = client.collection('config').document('system').get()
    if doc.exists:
        system = doc.to_dict()
        ret.update(system)
    else:
        logging.error(f'Failed to load config')
    return ret


def subscribe(client, channel, email):
    sub_id = gen_id(channel, email)
    client.collection('subscription').document(sub_id).set({
            'channel': channel,
            'email': email,
            'is_validated': False,
            'date_created': firestore.SERVER_TIMESTAMP,
            'date_modified': None
        })


def get_subscription(client, channel, email):
    ret = None
    sub_id = gen_id(channel, email)
    doc = client.collection('subscription').document(sub_id).get()
    if doc.exists:
        sub = doc.to_dict()
    return ret


def add_validation(client, code, channel, email, operation):
    sub_id = gen_id(channel, email)
    client.collection('validation').document(code).set({
            'sub_id': sub_id,
            'operation': operation,
            'is_used': False,
            'date_created': firestore.SERVER_TIMESTAMP,
            'date_modified': None
        })


def age_validation(client, channel, email):
    sub_id = gen_id(channel, email)
    docs = client.collection('validation').where('sub_id', '==', sub_id).stream()
    for doc in docs:
        val = doc.to_dict()
        if not val['is_used']:
            doc.reference.update({
                    'is_used': True,
                    'date_modified': firestore.SERVER_TIMESTAMP
                })


def remove_validation(client, threshold, batch):
    ret = 0
    docs = client.collection('validation') \
                 .where('date_created', '<', threshold) \
                 .order_by('date_created').limit(batch).stream()
    for doc in docs:
        doc.reference.delete()
        ret += 1
    return ret


def validate(client, code):
    doc1 = client.collection('validation').document(code).get()
    if not doc1.exists:
        raise InvalidCodeError
    val = doc1.to_dict()
    if val['is_used']:
        raise UsedCodeError
    doc2 = client.collection('subscription').document(val['sub_id']).get()
    sub = doc2.to_dict()
    if not doc2.exists:
        raise InvalidSubIdError
    if val['operation'] == 'SUBSCRIBE':
        doc2.reference.update({
                'is_validated': True,
                'date_modified': firestore.SERVER_TIMESTAMP
            })
    elif val['operation'] == 'UNSUBSCRIBE':
        doc2.reference.delete()
    doc1.reference.update({
            'is_used': True,
            'date_modified': firestore.SERVER_TIMESTAMP
        })
    return {'operation': val['operation'], 'channel': sub['channel']}


def get_urls(client, channel):
    ret = []
    docs = client.collection('history') \
                 .where('channel', '==', channel).stream()
    for doc in docs:
        his = doc.to_dict()
        for item in his['items']:
            ret.append(item['url'])
    return ret


def add_news(client, channel, url, title, is_notified=True):
    news_id = gen_id(channel, get_date_group())
    doc = client.collection('history').document(news_id).get()
    if doc.exists:
        his = doc.to_dict()
        doc.reference.update({
                'date_modified': firestore.SERVER_TIMESTAMP,
                'count': his['count'] + 1,
                'items': firestore.ArrayUnion([{
                        'url': url,
                        'title': title,
                        'is_notified': is_notified,
                    }])
            })
    else:
        client.collection('history').document(news_id).set({
                'channel': channel,
                'date_created': firestore.SERVER_TIMESTAMP,
                'date_modified': None,
                'count': 1,
                'items': [{
                        'url': url,
                        'title': title,
                        'is_notified': is_notified,
                    }]
            })


def remove_news(client, channel, threshold, batch):
    ret = 0
    if channel:
        docs = client.collection('history') \
                     .where('channel', '==', channel) \
                     .where('date_created', '<', threshold) \
                     .order_by('date_created').limit(batch).stream()
    else:
        docs = client.collection('history') \
                     .where('date_created', '<', threshold) \
                     .order_by('date_created').limit(batch).stream()
    for doc in docs:
        his = doc.to_dict()
        doc.reference.delete()
        ret += his['count']
    return ret

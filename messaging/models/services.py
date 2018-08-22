# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from toolz import merge, concatv, pluck

from messaging import helpers
from messaging.models.accounts import get_account_by_key
from messaging.dispatch import request


class Service(ndb.Model):
    name = ndb.StringProperty(required=True)
    provider = ndb.KeyProperty('Provider', required=True)
    vendor_key = ndb.StringProperty()
    quota = ndb.IntegerProperty()
    balance = ndb.IntegerProperty(default=0)
    statics = ndb.JsonProperty(default=[])
    modified_at = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        return merge(
            super(Service, self).to_dict(exclude=['provider', 'vendor_key']),
            {
                'id': self.key.urlsafe(),
                'account': self.key.parent().id(),
                'provider': self.provider.id(),
            }
        )

    def get_static(self, field):
        try:
            static_fields = pluck('field', self.statics)
            index = list(static_fields).index(field)
            return merge(
                super(Service, self).to_dict(include=['name']),
                {
                    'id': self.key.urlsafe(),
                },
                self.statics[index],
            )
        except ValueError:
            return None


def create(fields, site, body):
    account = ndb.Key('Account', site)
    provider = ndb.Key('Provider', body.get('provider'))
    if not account.get() or not provider.get():
        raise ReferenceError()
    return helpers.make_create(
        Service, concatv(fields, ['parent']),
    )(
        merge(body, {'provider': provider, 'parent': account})
    )


def update(fields, id, body):
    provider = body.get('provider')
    if provider and not ndb.Key('Provider', provider).get():
        raise ReferenceError()
    return helpers.make_update(Service, fields, urlsafe=True)(
        id,
        merge(body, {'provider': ndb.Key('Provider', provider)})
        if provider else body,
    )


def list_by_site(site):
    entities = Service.query(ancestor=ndb.Key('Account', site)) \
        .order(Service.modified_at) \
        .fetch(limit=helpers.QUERY_LIMIT)
    return map(lambda x: x.to_dict(), entities)


def put_static(id, static):
    service = ndb.Key(urlsafe=id).get()
    if not service:
        raise ReferenceError()
    field = static.get('field')
    service.statics = filter(
        lambda x: x.get('field') != field, service.statics,
    ) + [static]
    service.put()
    return service.get_static(field)


def get_static(id, field):
    service = ndb.Key(urlsafe=id).get()
    if not service:
        raise ReferenceError()
    static = service.get_static(field)
    if not static:
        raise ReferenceError()
    return static


def remove_static(id, field):
    service = ndb.Key(urlsafe=id).get()
    if not service:
        raise ReferenceError()
    service.statics = filter(
        lambda x: x.get('field') != field, service.statics,
    )
    service.put()
    return None
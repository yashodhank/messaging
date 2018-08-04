# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

from messaging import helpers


class Provider(ndb.Model):
    name = ndb.StringProperty(required=True)
    base_url = ndb.StringProperty(required=True)
    vendor_key = ndb.StringProperty(required=True)
    modified_at = ndb.DateTimeProperty(auto_now=True)


create = helpers.make_create(
    Provider, ['name', 'base_url', 'vendor_key'], 'name'
)
get = helpers.make_get(Provider)
list = helpers.make_list(Provider)
update = helpers.make_update(
    Provider, ['base_url', 'vendor_key']
)
delete = helpers.make_delete(Provider)
from marshmallow import Schema, fields

class BaseItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

class BaseStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str() 

class BaseTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class ItemSchema(BaseItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(BaseStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(BaseTagSchema()), dump_only=True)

class UpdateItemSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store = fields.Int()

class StoreSchema(BaseStoreSchema):
    items = fields.List(fields.Nested(BaseItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(BaseTagSchema()), dump_only=True)

class TagSchema(BaseTagSchema):
    store_id = fields.Int(load_only=True)
    items = fields.List(fields.Nested(BaseItemSchema()), dump_only=True)
    store = fields.Nested(BaseStoreSchema(), dump_only=True)


class ItemTagSchema(Schema):
     message = fields.Str()
     item = fields.Nested(BaseItemSchema)
     tag = fields.Nested(BaseTagSchema)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
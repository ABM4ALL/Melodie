import graphene


class Hero(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    age = graphene.Int()


class Query(graphene.ObjectType):
    hero = graphene.Field(Hero)

    def resolve_hero(self, info):
        return Hero(id=1, name='wsq', age=123)


schema = graphene.Schema(query=Query)
query = '''
    query something{
      hero {
        id
        name
        age
      }
    }
'''
result = schema.execute(query)
print(result)
print(result.data)

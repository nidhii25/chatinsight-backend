from bson import ObjectId

def fix_mongo(obj):
    if isinstance(obj, ObjectId):
        return str(obj)

    if isinstance(obj, list):
        return [fix_mongo(item) for item in obj]

    if isinstance(obj, dict):
        return {key: fix_mongo(value) for key, value in obj.items()}

    return obj

import redis
from pymongo import MongoClient

# Conexión a Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Conexión a MongoDB (para almacenar credenciales)
mongo_client = MongoClient('mongodb://mongo:27017/')
mongo_db = mongo_client['actividad4_db']
users_collection = mongo_db['users']

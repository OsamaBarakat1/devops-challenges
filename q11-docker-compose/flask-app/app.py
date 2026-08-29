import os
import redis
from flask import Flask, jsonify

app = Flask(__name__)

redis_host = os.environ.get("REDIS_HOST", "redis")
redis_port = int(os.environ.get("REDIS_PORT", 6379))

cache = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


@app.route("/")
def index():
    visits = cache.incr("visits")
    return jsonify(message="hello from flask", visits=visits)


@app.route("/health")
def health():
    cache.ping()
    return jsonify(status="ok"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, jsonify
import os
import redis
app = Flask(__name__)

password = os.environ.get('REDIS_PASSWORD')
redishost = os.environ.get('REDIS_URL')
health_status = True

@app.route('/')
def hello():
    try:
        r = redis.Redis(host=redishost, port=6379, db=0, password=password)
        r.set('foo', 'bar') 
        resp = r.get('foo')
        return f"<h1>redishost={redishost},password={password},redisres={resp}.</h2>"
    except:
        return f"<h1>redishost={redishost},password={password},redis=failed.</h2>"


@app.route('/health')
def health():
    if health_status:
        resp = jsonify(health="healthy")
        resp.status_code = 200
    else:
        resp = jsonify(health="unhealthy")
        resp.status_code = 500

    return resp


if __name__ == "__main__":
    app.run(debug=True)
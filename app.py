import logging
import json
import time
from flask import Flask, request, jsonify
from itertools import combinations
from rapidfuzz.distance.DamerauLevenshtein import normalized_similarity
from gevent import monkey
# monkey.patch_all()

app = Flask(__name__)
health_status = True
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_similar_account_pairs(posts, accounts, hashtag, min_similarity):
    # Filter posts by hashtag and exclude reposts
    account_ids = set()
    # Converting hashtags to lower case
    posts = [{k: (v.lower() if k == 'hashtags' else v) for k, v in posts_dict.items()} for posts_dict in posts]
    for post in posts:
        if all(k in post for k in ['hashtags', 'is_repost']) and not json.loads(post['is_repost'].lower()) and \
                hashtag.lower() in post['hashtags']:
            account_ids.add(post['author_id'])

    # Extract screen names from accounts
    hashtag_accts = [acct for acct in accounts if acct['id'] in list(account_ids)]

    # Iterate through combinations of relevant accounts and calculate similarity
    similar_account_pairs = []
    for account_1, account_2 in combinations(hashtag_accts, 2):
        screen_name1 = account_1['screen_name']
        screen_name2 = account_2['screen_name']
        similarity = normalized_similarity(screen_name1.lower(), screen_name2.lower())
        if similarity > min_similarity:
            similar_account_pairs.append((account_1['id'], account_2['id'], similarity))

    return similar_account_pairs


# New route for health check
@app.route('/health', methods=['GET'])
def health():
    if health_status:
        resp = jsonify(health="healthy")
        resp.status_code = 200
    else:
        resp = jsonify(health="unhealthy")
        resp.status_code = 500
    return resp


@app.route('/toggle')
def toggle():
    """Toggle the health_status to True/False depending on the situation."""
    global health_status
    health_status = not health_status
    logger.info('health_status is {}'.format(health_status))
    return jsonify(health_value=health_status)


@app.route('/get_similar_account_pairs', methods=['GET'])
def api_get_similar_account_pairs():
    # Get parameters from request
    st = time.time()
    try:
        req = json.loads(request.data)
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError("Unable to parse request, error: {}".format(e))
    except Exception as e:
        raise ValueError("Unknown, error: {}".format(e))
    # Failsafe, if any of the expected keys not found
    if not all(k in req.keys() for k in ['accounts', 'posts', 'hashtag']):
        return jsonify({'error': 'not all keys found, pls check input'})
    accounts = req['accounts']
    posts = req['posts']
    hashtag = req['hashtag']
    if 'min_similarity' in req.keys():
        min_similarity = req['min_similarity']
    else:
        min_similarity = 0.8

    # Call the function to get similar account pairs
    similar_account_pairs = get_similar_account_pairs(posts, accounts, hashtag, min_similarity)
    logger.info("Time taken to process the request is: {}".format(str(time.time()-st)))
    # Return the result as JSON
    return jsonify(similar_account_pairs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
    # app.run(debug=True)

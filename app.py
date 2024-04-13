import ast
import logging
from flask import Flask, request, jsonify
from itertools import combinations
from rapidfuzz.distance.DamerauLevenshtein import normalized_similarity
from gevent import monkey
monkey.patch_all()

app = Flask(__name__)
health_status = True


def get_similar_account_pairs(posts, accounts, hashtag, min_similarity):
    # Filter posts by hashtag and exclude reposts
    account_ids = set()
    for post in posts:
        print(post)
        if not post['is_repost'] and post['hashtags'] and hashtag in post['hashtags']:
            account_ids.add(post['author_id'])

    # Extract screen names from accounts
    hashtag_accts = [acct for acct in accounts if acct['id'] in list(account_ids)]

    # Iterate through combinations of relevant accounts and calculate similarity
    similar_account_pairs = []
    for account_1, account_2 in combinations(hashtag_accts, 2):
        screen_name1 = account_1['screen_name']
        screen_name2 = account_2['screen_name']
        similarity = normalized_similarity(screen_name1, screen_name2)
        if similarity > min_similarity:
            similar_account_pairs.append((account_1['id'], account_2['id']))

    return similar_account_pairs


# New route for health check
@app.route('/health')
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
    posts = ast.literal_eval(request.args.get('posts'))
    accounts = ast.literal_eval(request.args.get('accounts'))
    hashtag = request.args.get('hashtag')
    min_similarity_str = request.args.get('min_similarity')
    if min_similarity_str is None:
        min_similarity = 0.8  # Default value
    else:
        min_similarity = float(ast.literal_eval(min_similarity_str))
    # Call the function to get similar account pairs
    similar_account_pairs = get_similar_account_pairs(posts, accounts, hashtag, min_similarity)

    # Return the result as JSON
    return jsonify(similar_account_pairs)


def set_logger(logger_nm: str):
    logger_obj = logging.getLogger(logger_nm)
    logger_obj.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger_obj.addHandler(stream_handler)
    return logger


if __name__ == '__main__':
    logger = set_logger(__name__)
    app.run(debug=True)

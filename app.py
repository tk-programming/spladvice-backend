from flask import Flask, jsonify, request
from flask_cors import CORS
import supabase
import uuid
import os

# SupabaseプロジェクトのURLとアクセスキーを設定します
if os.environ.get('FLASK_ENV') == 'dev':
    supabase_url = os.environ.get('SUPABASE_URL_DEV')
    supabase_key = os.environ.get('SUPABASE_KEY_DEV')
else:
    supabase_url = os.environ.get('SUPABASE_URL_PROD')
    supabase_key = os.environ.get('SUPABASE_KEY_PROD')

# Supabaseクライアントを初期化します
supabase_client = supabase.create_client(supabase_url, supabase_key)

app = Flask(__name__)
CORS(app)

########################################## 新規会員登録 ##########################################
# 新規会員登録
@app.route('/register', methods=['POST'])
def register():
    userId = request.form.get('userId', type=str)
    password = request.form.get('password', type=str)
    displayName = request.form.get('displayName', type=str)
    response = supabase_client.table('user').insert(({"user_id": userId, "password": password, "display_name": displayName})).execute()
    return response.data


########################################## ログイン ##########################################

# ログイン
@app.route('/login', methods=['GET'])
def login():
    userId = request.args.get('userId', type=str)
    password = request.args.get('password', type=str)
    response = supabase_client.table('user').select('*').eq('user_id', userId).eq('password', password).execute()
    return response.data

# ログインユーザの記事を取得
@app.route('/searchByUserId', methods=['GET'])
def search_by_user_id():
    user_id = request.args.get('query', type=str)
    response = supabase_client.table('article').select('*, buki(*), user(*)').eq('author_id', user_id).execute()
    return response.data


########################################## ブキから検索 ##########################################

# ブキ一覧を取得
@app.route('/getBukis', methods=['GET'])
def get_bukis():
    response = supabase_client.table('buki').select('*').order('display_order').execute()
    return response.data

# 選択したブキの記事を取得
@app.route('/searchByBuki', methods=['GET'])
def search_by_buki():
    buki_id = request.args.get('query', type=str)
    response = supabase_client.table('article').select('*, buki(*), user(*)').eq('buki_id', buki_id).execute()
    return response.data


########################################## 記事ランキング ##########################################

# 記事ランキング
@app.route('/getArticleRanking')
def get_article_ranking():
    response = supabase_client.table('article').select('*, buki(*), user(*)').order('article_likes', desc=True).limit(10).execute()
    return response.data

########################################## 記事詳細 ##########################################
@app.route('/getArticleDetail')
def get_article_detail():
    article_id = request.args.get('query', type=str)
    response = supabase_client.table('article').select('*, buki(*), user(*)').eq('article_id', article_id).execute()
    return response.data

@app.route('/updateLikes', methods=['POST'])
def update_likes():
    articleId = request.form.get('articleId', type=str)
    increment = request.form.get('increment', type=str)  # 文字列として取得
    increment_bool = increment.lower() == 'true'  # 文字列をブール値に変換

    # いいね数を取得
    response = supabase_client.table('article').select("article_likes").eq('article_id', articleId).execute()
    print(response)
    articleLikes = response.data[0]["article_likes"]

    if increment_bool :
        response = supabase_client.table('article').update({'article_likes': articleLikes + 1}).eq('article_id', articleId).execute()
    else :
        response = supabase_client.table('article').update({'article_likes': articleLikes - 1}).eq('article_id', articleId).execute()
    
    return response.data


########################################## 記事新規投稿 ##########################################
@app.route('/registerArticle', methods=['POST'])
def register_article():
    articleId = generate_unique_string()
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    bukiId = data.get('bukiId')
    userId = data.get('userId')
    response = supabase_client.table('article').insert(({"article_id": articleId, "article_title": title, "article_content": content, "article_likes": 0, "buki_id": bukiId, "author_id": userId})).execute()
    return response.data

def generate_unique_string():
    while True:
        # ランダムなUUIDを生成
        random_uuid = str(uuid.uuid4())
        # 生成したUUIDがユニークであるかデータベースでチェック
        response = supabase_client.table('article').select('article_id').eq('article_id', random_uuid).execute()
        print(response)
        print(random_uuid)

        # ユニークなIDであれば、そのIDを返す
        if not response.data :
            return random_uuid

########################################## 記事編集 ##########################################

@app.route('/updateArticle', methods=['POST'])
def update_article():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    bukiId = data.get('bukiId')
    userId = data.get('userId')
    articleId = data.get('articleId')
    response = supabase_client.table('article').update(({"article_title": title, "article_content": content, "buki_id": bukiId,  "author_id": userId})).eq('article_id', articleId).execute()
    return response.data

########################################## 記事削除 ##########################################

@app.route('/deleteArticle', methods=['POST'])
def delete_article():
    articleId = request.form.get('articleId', type=str)
    response = supabase_client.table('article').delete().eq('article_id', articleId).execute()
    return response.data

########################################## main ##########################################

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
import requests
import base64
import json

app = Flask(__name__)

JWT_API = "https://jwtsemygen.vercel.app/token?key=SEMY&uid={uid}&password={password}"
INFO_API = "https://infosemy.vercel.app/ajay-info?uid={account_id}&region=IND"
HIT_API = "https://infopapa.vercel.app/info?uid={uid}&password={password}"

# JWT decode function
def decode_jwt(token):
    payload = token.split(".")[1]
    padding = '=' * (-len(payload) % 4)
    decoded = base64.urlsafe_b64decode(payload + padding)
    return json.loads(decoded)

@app.route("/infosemy")
def infosemy():

    uid = request.args.get("uid")
    password = request.args.get("password")

    if not uid or not password:
        return jsonify({"error": "uid & password required"}), 400

    try:
        # STEP 1️⃣ JWT generate
        jwt_res = requests.get(JWT_API.format(uid=uid, password=password)).json()

        if "token" not in jwt_res:
            return jsonify({"error": "JWT API failed"}), 500

        token = jwt_res["token"]

        # STEP 2️⃣ Decode JWT → account_id
        decoded = decode_jwt(token)
        account_id = decoded["account_id"]

        # STEP 3️⃣ Hit Info API
        info = requests.get(INFO_API.format(account_id=account_id)).json()

        basic = info["basicInfo"]

        nickname = basic["nickname"]
        region = basic["region"]
        level = basic["level"]
        likes = basic["liked"]
        account_id_final = basic["accountId"]

        # STEP 4️⃣ Hit last API (response ignore)
        try:
            requests.get(HIT_API.format(uid=uid, password=password))
        except:
            pass

        # STEP 5️⃣ Final Response
        return jsonify({
            "Nickname": nickname,
            "Region": region,
            "Level": level,
            "Likes": likes,
            "Account_Id": account_id_final
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel entry
app = app
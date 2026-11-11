import time
import requests

TG_BOT_TOKEN = "9295785565:AAE7EnzFMwja3gIZz8fKZxtKbGhCYDiqbAA"
TG_CHANNEL = "@match_test_kz"

TEST_ON_START = True
GAME_ID = "401909960"
sent_events = set()
match_state = {"started": False, "ft_sent": False}


def build_emotional_post(text):
    return (
        f"🏀 ОЙЫН ЖАҢАЛЫҒЫ!\n\n"
        f"{text}\n\n"
        f"📲 @match_test_kz"
    )


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={"chat_id": TG_CHANNEL, "text": text})
    if res.status_code == 200:
        print("✅ Пост @match_test_kz каналына сәтті жіберілді!")
    else:
        print("❌ Телеграм қатесі:", res.text)


def run_test_post():
    print("⏳ ESPN сынақ хабарламасы жіберілуде...")
    post = build_emotional_post("🔥 Матч бақылауға алынды! Бот сәтті қосылды.")
    send_to_telegram(post)


def check_espn_game():
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={GAME_ID}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        header = data.get("header", {})
        competitions = header.get("competitions", [])
        if not competitions:
            print("⏳ Матч деректері әлі шықпады...")
            return

        comp = competitions[0]
        status_type = comp.get("status", {}).get("type", {}).get("state")
        
        competitors = comp.get("competitors", [])
        home_team, away_team = "Home", "Away"
        home_score, away_score = "0", "0"

        for c in competitors:
            if c.get("homeAway") == "home":
                home_team = c.get("team", {}).get("displayName", "Home")
                home_score = c.get("score", "0")
            else:
                away_team = c.get("team", {}).get("displayName", "Away")
                away_score = c.get("score", "0")

        score_text = f"{home_team} {home_score} : {away_score} {away_team}"

        if status_type == "in" and not match_state["started"]:
            post = build_emotional_post(f"🔥 МАТЧ БАСТАЛДЫ!\n\n⚔️ {score_text}")
            send_to_telegram(post)
            match_state["started"] = True

        plays = data.get("plays", [])
        for play in plays:
            text_desc = play.get("text", "")
            play_id = play.get("id", "")
            
            if play_id and play_id not in sent_events:
                if any(keyword in text_desc.lower() for keyword in ["makes", "three point", "dunk", "fouled"]):
                    post = build_emotional_post(f"⚡️ {text_desc}\n\n📊 Есеп: {score_text}")
                    send_to_telegram(post)
                    sent_events.add(play_id)

        if status_type == "post" and not match_state["ft_sent"]:
            post = build_emotional_post(f"🏁 МАТЧ АЯҚТАЛДЫ!\n\n📊 Қорытынды есеп: {score_text}")
            send_to_telegram(post)
            match_state["ft_sent"] = True

    except Exception as e:
        print("⚠️ ESPN қатесі:", e)


if __name__ == "__main__":
    print("🤖 ESPN NBA боты іске қосылды!")
    if TEST_ON_START:
        run_test_post()

    while True:
        try:
            check_espn_game()
        except Exception as e:
            print("⚠️ Қате:", e)
        time.sleep(60)

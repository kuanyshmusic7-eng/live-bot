import time
import requests

TG_BOT_TOKEN = "9295785565:AAE7EnzFMwja3gIZz8fKZxtKbGhCYDiqbAA"
TG_CHANNEL = "@match_test_kz"

MATCH_ID = "6577364"
sent_events = set()
match_state = {"started": False, "ft_sent": False}


def build_emotional_post(text):
    return (
        f"⚽️ ФУТБОЛ ЖАҢАЛЫҒЫ!\n\n"
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


def check_fotmob_match():
    url = f"https://www.fotmob.com/api/matchDetails?matchId={MATCH_ID}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        
        header = data.get("header", {})
        teams = header.get("teams", [])
        if len(teams) >= 2:
            home_team = teams[0].get("name", "Home")
            away_team = teams[1].get("name", "Away")
            home_score = teams[0].get("score", 0)
            away_score = teams[1].get("score", 0)
        else:
            home_team, away_team = "Home", "Away"
            home_score, away_score = 0, 0

        score_text = f"{home_team} {home_score} : {away_score} {away_team}"
        
        status = header.get("status", {})
        is_started = status.get("started", False)
        is_finished = status.get("finished", False)
        
        if is_started and not match_state["started"]:
            post = build_emotional_post(f"🔥 МАТЧ БАСТАЛДЫ!\n\n⚔️ {score_text}")
            send_to_telegram(post)
            match_state["started"] = True

        content = data.get("content", {})
        match_facts = content.get("matchFacts", {})
        events = match_facts.get("events", {}).get("events", [])
        
        for event in events:
            event_id = str(event.get("id", ""))
            if event_id and event_id not in sent_events:
                etime = event.get("time", "")
                etype = event.get("type", "")
                player_name = event.get("playerName", "")
                team_name = event.get("teamName", "")
                
                if etype in ["Goal", "YellowCard", "RedCard"]:
                    emoji = "⚽️ ГОЛ!" if etype == "Goal" else ("🟨 Сары қағаз" if etype == "YellowCard" else "🟥 Қызыл қағаз")
                    post = build_emotional_post(f"{emoji} ({etime}')\n👤 {player_name} ({team_name})\n\n📊 Есеп: {score_text}")
                    send_to_telegram(post)
                    sent_events.add(event_id)

        if is_finished and not match_state["ft_sent"]:
            post = build_emotional_post(f"🏁 МАТЧ АЯҚТАЛДЫ!\n\n📊 Қорытынды есеп: {score_text}")
            send_to_telegram(post)
            match_state["ft_sent"] = True

    except Exception as e:
        print("⚠️ FotMob қатесі:", e)


if __name__ == "__main__":
    print("🤖 Футбол боты іске қосылды!")
    post = build_emotional_post("🔥 Футбол матчы сәтті бақылауға алынды!")
    send_to_telegram(post)

    while True:
        try:
            check_fotmob_match()
        except Exception as e:
            print("⚠️ Қате:", e)
        time.sleep(60)

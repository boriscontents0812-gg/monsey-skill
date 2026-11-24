import json
B = "../B-roll/"  # your noir stills folder, relative to the post folder
def P(img, cy, text): return {"type": "photo", "photo": B + img, "text": text, "fx": 0.5, "fy": 0.3 if "p01" in img else 0.5, "cy": cy}
H, M = "her", "me"
S = [
 P("p31n.jpg", .62, "POV: She forgot your\nbirthday, but liked his\npost at 12:01."),
 [(H,"heyy what are you doing tonight"),(M,"Nothing much."),(H,"wanna come over? i'm bored"),(M,"Not tonight.")],
 [(H,"why not"),(M,"Long day."),(H,"you've been weird all day"),(M,"Have I?")],
 [(H,"yeah. did something happen?"),(M,"Nothing important."),(H,"ok now i know something happened")],
 P("p30n.jpg", .66, "She asked what happened.\nThe answer was nothing.\nThat was the problem."),
 [(H,"just tell me"),(M,"What was yesterday's date?"),(H,"the 14th? why"),(M,"No reason.")],
 [(H,"wait"),(H,"oh my god"),(H,"it was your birthday"),(M,"Yeah.")],
 [(H,"i'm so sorry"),(H,"i've been so busy this week"),(M,"You weren't busy at 12:01.")],
 P("p17n.jpg", .66, "I didn’t need a gift.\nI needed to be the first\nname she thought of.\nI wasn’t even the last."),
 [(H,"what do you mean"),(M,"You liked Jake's post at midnight."),(H,"that's not the same thing")],
 [(H,"you're seriously mad over a like?"),(M,"I'm not mad."),(H,"then what is this")],
 {"type": "card", "line": "It's not about the like. It's about where your attention goes first."},
 [(H,"..."),(H,"that's not fair"),(M,"Is it wrong though?"),(H,"i didn't mean anything by it")],
 P("p21n.jpg", .66, "People don’t forget\nwhat matters to them.\nThey just show you\nwhat doesn’t."),
 [(H,"let me make it up to you"),(M,"You don't have to."),(H,"i want to. dinner tomorrow?"),(M,"I'm busy tomorrow.")],
 [(H,"with who"),(M,"Myself."),(H,"you're punishing me"),(M,"I'm just not waiting anymore.")],
 [(H,"waiting for what"),(M,"For you to remember me without being reminded.")],
 P("p08n.jpg", .66, "Every year I counted\nthe hours until her text.\nThis year I stopped counting."),
 [(H,"it's one day"),(M,"It was one day. Then one plan. Then one week."),(H,"so this has been building up"),(M,"For a while.")],
 [(H,"why didn't you say something"),(M,"I did. You said I was overthinking."),(H,"..."),(H,"i remember")],
 [(H,"so what now"),(M,"Now nothing."),(H,"you don't want me anymore?"),(M,"I want someone who wants me back.")],
 P("p39n.jpg", .66, "Love isn’t a big gesture\nonce a year. It’s remembering\nsomeone on an ordinary\nTuesday."),
 [(H,"i do want you"),(M,"Then why did I have to tell you it was my birthday?"),(H,"...")],
 [(H,"i messed up"),(M,"I know."),(H,"can we talk tomorrow at least"),(M,"We're talking now.")],
 [(H,"please don't do this"),(M,"I'm not doing anything. I'm just done reminding you I exist."),(H,"happy birthday"),(M,"Thanks.")],
 P("p01n.jpg", .66, "The text I waited all day\nfor finally came. It just\ndidn’t mean anything\nanymore."),
]
t, prev, out = 22 * 60 + 31, None, []  # clock starts 22:31
for s in S:
    if isinstance(s, dict): out.append(s); continue
    msgs, rep = [], prev is not None and s[0][1] == prev[1]
    for i, (who, txt) in enumerate(s):
        if i == 0 and rep: tm = prev[2]
        else: tm = f"{t//60 % 24:02d}:{t%60:02d}"; t += 1 if who == H else 0
        msgs.append({"sender": who, "text": txt.replace("'", "’"), "time": tm})
    prev = (s[-1][0], s[-1][1], msgs[-1]["time"])
    out.append({"type": "chat", "msgs": msgs, **({"repeat_first": True} if rep else {})})
out.append({"type": "card", "line": "end card"})
assert len(out) == 27 and out[11]["type"] == "card"
json.dump({"header_slides": 1, "square": True, "slides": out}, open("story.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(prev[2])

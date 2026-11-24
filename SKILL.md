---
name: mONSEY
description: Make a Rizz-promo TikTok photo-story post in the @itext_ style. That means a 27-28 slide "stopped chasing" WhatsApp story with noir Patrick Jane narrator stills, real iOS WhatsApp chat slides, the official Rizz promo card at slide 12 and the Rizz "Get your replies" end card, saved as numbered slides in a new post folder with a title and caption. "mONSEY" is the user's keyword for this skill, so use it whenever they say "mONSEY" in any capitalisation. Also use it for "make another one like last time", "itext style", a psychology texting slideshow, a Rizz promo chat story, or redoing an @itext_ post, even if they never say "skill".
---

# mONSEY: itext-style Rizz chat story

Each post is a sad, calm "he stopped chasing, she notices too late" story told in WhatsApp screenshots. The screenshots are broken up by Patrick Jane (The Mentalist) narrator stills in a noir look.

- `TOOLS`: the `tools/` folder next to this file. Every command below runs from there.
- Posts folder: wherever the user keeps their posts. Ask once if you don't know it, for example `~/Psychology Texting`. Each post gets its own subfolder, and the stills live in `<posts folder>/B-roll`.
- First run: check that the setup in README.md is done. That means the pip packages, `TOOLS/SF-Pro-Text-Regular.otf`, `TOOLS/Proxima-Nova-Semibold.otf`, and `~/.lama/lama_fp32.onnx` (only needed for cleaning TikTok stills).

## 0. Rules that never bend

- **Script first.** Write the full script, then stop and wait for "Script is good" or another clear go-ahead before you build anything.
- **Check for repeats first.** Before pitching, grep the old `story.json` files in the posts folder for the same hook or theme. The user hates posts that read as repeats.
- **Every Jane photo is noir** (`noir.py`).
- **Use fresh stills every post.** Never reuse a still from an earlier post (see step 3).
- **Slide count and card position:** 27-28 slides, with the Rizz card at **slide 12** and the end card last.
- **No emoji in chats.** The renderer draws them as a box.
- Don't delete the user's files without asking.

## 1. Script format

| Part | Rule |
|---|---|
| Slide 1 | A noir Jane still with a "POV: ..." hook of about 20 characters or less per line, broken with `\n` |
| Chats | 3-4 bubbles each. "her" texts in lowercase and casual; "me" is calm, short, capitalised, and never begs |
| Repeat line | A chat may start with the previous chat's last line. The script detects this and repeats it with the same time |
| Narrator | A noir Jane still with one calm, sad, first-person line every 3-4 chats |
| Card (slide 12) | The chat before it ends on her message. The card line is one short psychology sentence that changes her mind: no instructions, no flirting. The next chat continues from it |
| Ending | Sad or quiet: he walks away, or she realises too late. The last narrator line is the payoff |
| End card | `assets/end-card.png` (Rizz "Get your replies") |

Show the script to the user as plain slide lines (Slide 1: hook / Slide 2: chat ... / Slide 12: RIZZ CARD "line" ...) along with the proposed title and caption.

**Title:** short and lowercase, first person ("she forgot my birthday", "I almost let her go").
**Caption:** `@RIZZ APP <one short life lesson>. Link in bio #texting #sad #breakup`. You can swap in `#mentalist #darkpsychology`.

## 2. Build the story

1. Create `<posts folder>/<Title Case Name>/`.
2. Copy `scripts/make_story_template.py` to `make_story.py` in the new folder and fill in `S`:
   - `P(img, cy, text)` makes a photo slide. `img` is a file in B-roll. `cy` is the caption's vertical centre (0-1); .62-.66 suits most stills. Use `fy` to move the crop focus (for example .3 for a high face).
   - A list of `(H|M, "text")` tuples makes a chat.
   - `{"type": "card", "line": "..."}` is the Rizz card.
   - Set the clock start (`t = 22 * 60 + 31`). Her messages add 1 minute each.
   - Fix the `assert` to the real slide count and card index (`out[11]` = slide 12).
3. Run `python make_story.py` inside the post folder. That writes story.json.
4. In the same folder, run `python TOOLS/wa_render.py story.json .`. It writes `slide-NN.png` at 1320x1320, with the header on the first chat only.

## 3. Fresh noir Jane stills

1. Search Pinterest for "patrick jane" or "simon baker the mentalist". Download the `i.pinimg.com/736x/...` images into a new folder.
2. Skip collages, red-carpet shots, pins with text, and smiling stills meant for sad lines.
3. Check for stills that were already used with `python TOOLS/dedupe.py <new folder> <posts folder>/B-roll`. Drop any still marked `USED`.
4. Move the keepers into B-roll as `pNN.jpg` and make the noir versions: `python TOOLS/noir.py pNN.jpg pNNn.jpg`. Use the `*n.jpg` files in the story.
5. To get stills from an @itext_ post instead:
   - On the post page, map each `img[src*=photomode]` to a line of "host id expires sig".
   - Download them with `bash TOOLS/tt_dl.sh outdir < lines`.
   - Remove the burned-in text with `python TOOLS/lama_clean.py in out`, which prints the `cy` value. Skip any still where the text crosses the face, because LaMa smears it.
   - Remove the @itext watermark with `python TOOLS/lama_box.py img .42 .76 .60 .89`.
6. Add the used file names to `B-roll/used.txt` so the next post avoids them.

## 4. Rizz card (slide 12)

1. Start the card server in the background: `python TOOLS/card_server.py "<post folder>"` (127.0.0.1:8766).
2. Open https://rizz-template.vercel.app/ in a browser tab you can run JavaScript in. The tab must be in front, because background tabs don't render.
3. Set `CHAT` (slide-11.png), `LINE` and `OUT` in `scripts/card.js` and run it in that tab. It uploads the chat, sets the line and POSTs `rizz-card-raw.png`.
4. Flatten it onto black and clean up:
   ```python
   from PIL import Image; im = Image.open("rizz-card-raw.png").convert("RGBA")
   bg = Image.new("RGBA", im.size, (0, 0, 0, 255)); bg.alpha_composite(im); bg.convert("RGB").save("slide-12-rizz-card.png")
   ```
   Then delete `rizz-card-raw.png` and the renderer's placeholder `slide-12.png`, and stop the server.

## 5. End card

Copy `assets/end-card.png` to `slide-NN-end-card.png` (NN = the last slide) and delete the placeholder `slide-NN.png`.

## 6. Check and deliver

1. Make a contact sheet with `python TOOLS/story_sheet.py <post folder>` and look at it. Check for:
   - captions over faces
   - boxes where emoji were
   - a wrong slide order
   - smiling stills on sad lines
   - the card sitting at 12
2. Show the user every slide in posting order.
3. Give the **title** and the **caption**, ready to paste. Remind them to add a trending sound.

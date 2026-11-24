# mONSEY skill

This is a Claude Code skill. It makes itext-style Rizz promo chat stories for TikTok: WhatsApp chat slides, noir Patrick Jane stills, the Rizz card at slide 12, and an end card.

## Install

1. Clone the repo into your Claude skills folder:
   ```
   git clone https://github.com/boriscontents0812-gg/monsey-skill.git ~/.claude/skills/mONSEY
   ```
2. Install the Python packages (Python 3.10+):
   ```
   pip install -r ~/.claude/skills/mONSEY/requirements.txt
   ```
3. Put the two fonts in `~/.claude/skills/mONSEY/tools/`. They aren't in the repo because their licences don't allow sharing:
   - `SF-Pro-Text-Regular.otf`: free from https://developer.apple.com/fonts/ (SF Pro).
   - `Proxima-Nova-Semibold.otf`: Proxima Nova Semibold, from Adobe Fonts or a licence you own.
4. Optional: you only need this to clean text off @itext_ stills. Download the LaMa model (about 200 MB) to `~/.lama/lama_fp32.onnx`, from https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx.

## Use

Open Claude Code and say **"mONSEY"**. Claude asks where your posts folder is, writes a script, and builds the slides once you approve the script.

Keep your stills in `<posts folder>/B-roll`.

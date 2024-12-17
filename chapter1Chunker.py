import os, re, shutil
from config import OPENAI_API_KEY

# ---- 1) Load the text ----
with open("interpretationOfDreams.txt", "r", encoding="utf-8", errors="ignore") as f:
    full_text = f.read()

# ---- 2) Robust anchors for Chapter I and II (match Gutenberg spacing) ----
chap_i_re  = re.compile(
    r"(?m)^[ \t]*I[ \t]*\n(?:[ \t]*\S.*\n){0,4}?[ \t]*THE SCIENTIFIC LITERATURE ON THE PROBLEMS OF THE DREAM\b",
    re.IGNORECASE
)
chap_ii_re = re.compile(
    r"(?m)^[ \t]*II[ \t]*\n(?:[ \t]*\S.*\n){0,4}?[ \t]*METHOD OF DREAM INTERPRETATION\b",
    re.IGNORECASE
)

m_i  = chap_i_re.search(full_text)
m_ii = chap_ii_re.search(full_text)

if not m_i:
    raise RuntimeError("Could not find Chapter I header. Check the file formatting.")
if not m_ii:
    raise RuntimeError("Could not find Chapter II header. Check the file formatting.")

start_i = m_i.start()          # beginning of the 'I' line
start_ii = m_ii.start()        # beginning of the 'II' line

chapter_i_text = full_text[start_i:start_ii]

# ---- 3) Split Chapter I into paragraphs ----
paragraphs = [p.strip() for p in chapter_i_text.split("\n\n") if p.strip()]

# Optional: drop the banner paragraph (the one that just holds the Chapter I lines)
# Keep it if you want it in Chunk 1; drop it if you want only body text.
if re.match(r"(?is)^i\s+the scientific literature on the problems of the dream", paragraphs[0].replace("\n"," ").strip()):
    paragraphs = paragraphs[1:]

# ---- 4) Fixed 4-paragraph chunks ----
chunk_size = 4
chunks = [paragraphs[i:i+chunk_size] for i in range(0, len(paragraphs), chunk_size)]

# ---- 5) Write files with headings ----
outdir = "chapter1_chunks"
os.makedirs(outdir, exist_ok=True)

for idx, chunk in enumerate(chunks, 1):
    heading = f"Chunk {idx}: Freud, Interpretation of Dreams — Chapter I\n\n"
    body = "\n\n".join(chunk)
    with open(os.path.join(outdir, f"chunk{idx}.txt"), "w", encoding="utf-8") as f:
        f.write(heading + body)

# ---- 6) Zip them up ----
shutil.make_archive("chapter1_chunks", "zip", outdir)
print(f"Created {len(chunks)} chunk files -> chapter1_chunks.zip")

import json, re, subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []
def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond: fails.append(msg)

html = open(ROOT + "/index.html").read()
ok("assets/anim-master.webp" in html, "index references anim-master.webp")
for a in ("anim-master.webp", "hana.jpg", "kaze.jpg", "elm.jpg"):
    ok(os.path.exists(ROOT + "/assets/" + a), "asset exists: " + a)
    ok(os.path.getsize(ROOT + "/assets/" + a) > 3000, "asset non-trivial: " + a)
m = re.search(r"<script>\nvar MODE(.*?)</script>", html, re.S)
ok(m is not None, "main script found")
if m:
    open("/tmp/_nonbi_check.js", "w").write("var MODE" + m.group(1))
    r = subprocess.run(["node", "--check", "/tmp/_nonbi_check.js"], capture_output=True, text=True)
    ok(r.returncode == 0, "JS syntax valid" + ("" if r.returncode == 0 else ": " + r.stderr[:200]))
S = json.load(open(ROOT + "/data/ikebukuro.json"))
ok(len(S) == 144, "data has 144 shops (got %d)" % len(S))
ok(all(s["n"] and s["a"] for s in S), "every shop has name + address")
HIRA = set("はがをにへともでしてくなりますやよかねぞわ")
KATA = set(chr(c) for c in range(0x30A1, 0x30F7))
def is_zh(t):
    if not t or len(t) < 6: return False
    if any(c in HIRA for c in t): return False
    if any(c in KATA for c in t): return False
    return any('一' <= c <= '鿿' for c in t)
ok(not any(is_zh(s["w"]) or is_zh(s["s"]) for s in S), "all user-visible text is Japanese (no Chinese fields)")
ok(sum(1 for s in S if s["gs"] and s["ts"]) == 17, "dual-score shops == 17")
ok(sum(1 for s in S if s["ts"]) == 142, "tabelog-scored == 142")
ok(len(set(s["id"] for s in S)) == 144, "ids unique")
ok(os.path.exists(ROOT + "/version.txt"), "version.txt present")
print("RESULT:", "ALL PASS" if not fails else "%d FAILURES" % len(fails))
sys.exit(1 if fails else 0)

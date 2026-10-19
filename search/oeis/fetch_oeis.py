"""Fetch OEIS search result pages (JSON) for a query into a cache dir."""
import json, sys, time, urllib.parse, urllib.request, os

def fetch(query, outdir, max_pages=30, sleep=1.0):
    os.makedirs(outdir, exist_ok=True)
    out = []
    for p in range(max_pages):
        url = "https://oeis.org/search?" + urllib.parse.urlencode({"q": query, "fmt": "json", "start": 10 * p})
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research script)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                txt = r.read().decode()
        except Exception as e:
            print("ERR", url, e, file=sys.stderr); break
        data = json.loads(txt)
        if not data:
            break
        out.extend(data)
        time.sleep(sleep)
    return out

if __name__ == "__main__":
    query, outfile, pages = sys.argv[1], sys.argv[2], int(sys.argv[3])
    res = fetch(query, os.path.dirname(outfile) or ".", pages)
    json.dump(res, open(outfile, "w"))
    print(query, len(res))

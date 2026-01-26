
filename = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"
try:
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "name: wikidata" in line:
                print(f"[{i+1}] {line.strip()}")
except Exception as e:
    print(e)

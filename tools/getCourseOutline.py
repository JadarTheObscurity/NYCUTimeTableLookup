import json
from NYCUTimeTableCrawler import NYCUTimeTableCrawler

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
with open('1151.json', 'r', encoding='utf-8') as f:
    result = json.load(f)

threads = []
outputs = [None] * len(result)
nycuTimeTableCrawler = NYCUTimeTableCrawler(115, 1)


import requests
def fetch_outline(course):
    course_id = course["cos_id"]
    response = nycuTimeTableCrawler.getOutline(course_id)
    outline = "" if not response else response.get("crs_outline", "")
    return course, outline

# with ThreadPoolExecutor(max_workers=10) as executor:
#     result = list(tqdm(executor.map(fetch_outline, result), total=len(result)))

MAX_RETRY=3

def crawl_outlines(result):
    pending = [(course, 1) for course in result]  # (data, attempt)
    final_result = []

    with ThreadPoolExecutor(max_workers=20) as executor:

        while pending:
            next_round = []
            futures = []

            future_to_task = {
                executor.submit(fetch_outline, course): (course, attempt)
                for course, attempt in pending
            }

            for future in tqdm(as_completed(future_to_task)):
                course, attempt = future_to_task[future]

                try:
                    _, outline = future.result()
                    course["crs_outline"] = outline
                    final_result.append(course)
                except requests.exceptions.RequestException:
                    if attempt < MAX_RETRY:
                        next_round.append((course, attempt + 1))
                    else:
                        course["crs_outline"] = ""
                        final_result.append(course)
                        print(f"Failed: {course['cos_id']}")

            pending = next_round

    return final_result

result = crawl_outlines(result)
with open('1151_outline.json', "w", encoding="utf8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
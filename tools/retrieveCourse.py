from NYCUTimeTableCrawler import NYCUTimeTableCrawler
import json

timeTableUrl = "https://timetable.nycu.edu.tw/"

# nycuTimeTableCrawler = NYCUTimeTableCrawler(112, 1, 112, 1)
# nycuTimeTableCrawler.saveDepartmentIdAndPath("departmentPath.json")
courseParams = None
with open("departmentPath.json", "r") as f:
    courseParams = json.load(f)

print(courseParams[0])
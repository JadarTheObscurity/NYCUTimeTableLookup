from NYCUTimeTableCrawler import NYCUTimeTableCrawler
import logging
from tqdm import tqdm
import json

timeTableUrl = "https://timetable.nycu.edu.tw/"

nycuTimeTableCrawler = NYCUTimeTableCrawler(113, 1, 113, 1)

def extraceCourseInfo(courseDetail, coursePath:str):
    courseInfoList = []
    key = []
    """
    1: 本系所開設課程
    2: 其他相關教學單位課程
    """
    if "1" in courseDetail.keys():
        key.append("1")
    if "2" in courseDetail.keys():
        key.append("2")
    
    for k in key:
        # Iterate through all courses
        for courseId in courseDetail[k].keys():
            courseInfo = {}
            # add course path
            courseInfo["coursePath"] = coursePath
            # get basic information
            for courseAttribute in courseDetail[k][courseId].keys():
                courseInfo[courseAttribute] = courseDetail[k][courseId][courseAttribute]
            # get tags
            courseInfo["costype"] = []
            for type in courseDetail["costype"][courseId].keys():
                # check if type have "_"
                if "_"  in type:
                    courseInfo["costype"].append(type.split("_")[1])
                else: 
                    courseInfo["costype"].append(type)
            # get language
            courseInfo["language"] = courseDetail["language"][courseId]["授課語言代碼"]

            courseInfoList.append(courseInfo)

    return courseInfoList


courseCount = 0
# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(handlers=[logging.FileHandler('example.log', 'w', 'utf-8')], level=logging.DEBUG)

with open("departmentPath.json", "r", encoding="utf8") as f:
    courseParams = json.load(f)
result = []
for i in tqdm(range(0, len(courseParams))):
    coursePath = courseParams[i]["departmentPath"]
    departmentId = courseParams[i]["departmentId"] 
    print(f"Find course {i} under {coursePath}, currently have {courseCount} courses")
    depCourseDetail = nycuTimeTableCrawler.getCourseList(departmentId)
    if len(depCourseDetail) == 0:
        logging.info(f"No course found in {coursePath}")
        continue
    for courseDetail in depCourseDetail.values():
        # print(courseDetail['dep_cname'])
        courseInfoList = extraceCourseInfo(courseDetail, coursePath)
        result += courseInfoList
        courseCount = len(result)


print(f"Total course count: {courseCount}")
file_name = f"{nycuTimeTableCrawler.acysem}_{nycuTimeTableCrawler.acysemend}.json"
with open(file_name, "w", encoding="utf8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
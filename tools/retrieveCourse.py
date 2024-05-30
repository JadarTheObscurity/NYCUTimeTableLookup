from NYCUTimeTableCrawler import NYCUTimeTableCrawler
import threading
import logging
from tqdm import tqdm
import json

timeTableUrl = "https://timetable.nycu.edu.tw/"

nycuTimeTableCrawler = NYCUTimeTableCrawler(113, 1)

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

print(f"Get department Id and Path")
courseParams = nycuTimeTableCrawler.getDepartmentIdAndPath()

courseDetails = {k:None for k in range(0, len(courseParams))}
def getCourseDetail(courseParams, i):
    departmentId = courseParams[i]["departmentId"] 
    depCourseDetail = nycuTimeTableCrawler.getCourseList(departmentId)
    courseDetails[i] = depCourseDetail

threads = []
print(f"Create http request for course detail.")
for i in tqdm(range(0, len(courseParams))):
    thread = threading.Thread(target=getCourseDetail, args=(courseParams, i))
    thread.start()
    threads.append(thread)
# Wait for all threads to finish
print(f"Waiting for http response for course detail.")
for thread in tqdm(threads):
    thread.join()

result = []
for idx, depCourseDetail in courseDetails.items():
    coursePath = courseParams[idx]["departmentPath"]
    if len(depCourseDetail) == 0:
        logging.info(f"No course found in {coursePath}")
        continue
    for courseDetail in depCourseDetail.values():
        # print(courseDetail['dep_cname'])
        courseInfoList = extraceCourseInfo(courseDetail, coursePath)
        result += courseInfoList
print(f"Total course count: {len(result)}")
# Dedupe
unique_course = {}
for course in result:
    cos_id = course['cos_id']
    if cos_id in unique_course.keys():
        if isinstance(unique_course[cos_id]['coursePath'], str):
           unique_course[cos_id]['coursePath'] = [unique_course[cos_id]['coursePath'], course['coursePath']]
        else:
            unique_course[cos_id]['coursePath'].append(course['coursePath'])
    else:
        unique_course[cos_id] = course
        unique_course[cos_id]['coursePath'] = [unique_course[cos_id]['coursePath'], course['coursePath']]
result = list(unique_course.values())
print(f"Total course count after dedup: {len(result)}")

# Retrieve course outline
thread_num = 512
for i in tqdm(range(0, len(result), thread_num)):
    def getCourseOutline(key):
        global result
        courseId = result[key]['cos_id']
        response = nycuTimeTableCrawler.getOutline(courseId)
        outline = "" if not response else response["crs_outline"]
        result[key]['crs_outline'] = outline
    threads = []
    end_idx = min(thread_num, len(result) - i)
    for j in range(0, end_idx):
        thread = threading.Thread(target=getCourseOutline, args=(i + j,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

file_name = f"{nycuTimeTableCrawler.acysem}.json"
with open(file_name, "w", encoding="utf8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
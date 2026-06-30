from NYCUTimeTableCrawler import NYCUTimeTableCrawler
import threading
import logging
from tqdm import tqdm
import json
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

timeTableUrl = "https://timetable.nycu.edu.tw/"


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

def fetch_outline(nycuTimeTableCrawler, course):
    course_id = course["cos_id"]
    response = nycuTimeTableCrawler.getOutline(course_id)
    outline = "" if not response else response.get("crs_outline", "")
    return course, outline

# with ThreadPoolExecutor(max_workers=10) as executor:
#     result = list(tqdm(executor.map(fetch_outline, result), total=len(result)))


def crawl_outlines(nycuTimeTableCrawler, result):
    MAX_RETRY=3
    pending = [(course, 1) for course in result]  # (data, attempt)
    final_result = []

    with ThreadPoolExecutor(max_workers=20) as executor:

        while pending:
            next_round = []

            future_to_task = {
                executor.submit(fetch_outline, nycuTimeTableCrawler, course): (course, attempt)
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


def crawl_all_course(year, semester):
    nycuTimeTableCrawler = NYCUTimeTableCrawler(year, semester)
    # courseCount = 0
    # logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    # logging.basicConfig(handlers=[logging.FileHandler('example.log', 'w', 'utf-8')], level=logging.DEBUG)

    print(f"Get department Id and Path")
    courseParams = nycuTimeTableCrawler.getDepartmentIdAndPath()


    print(f"Get courses in [{len(courseParams)}] departments")
    courseDetails = {k:None for k in range(0, len(courseParams))}
    def getCourseDetail(courseParams, idx):
        departmentId = courseParams[idx]["departmentId"] 
        depCourseDetail = nycuTimeTableCrawler.getCourseList(departmentId)
        return depCourseDetail
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {
            executor.submit(getCourseDetail, courseParams, idx): (idx)
            for idx in range(len(courseParams))
        }

        for future in tqdm(as_completed(future_to_task)):
            idx = future_to_task[future]
            depCourseDetail = future.result()
            courseDetails[idx] = depCourseDetail

    # courseDetails = {k:None for k in range(0, len(courseParams))}
    # def getCourseDetail(courseParams, i):
    #     departmentId = courseParams[i]["departmentId"] 
    #     depCourseDetail = nycuTimeTableCrawler.getCourseList(departmentId)
    #     courseDetails[i] = depCourseDetail
    # for i in tqdm(range(0, len(courseParams))):
    #     getCourseDetail(courseParams, i)

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
    # thread_num = 512
    # for i in tqdm(range(0, len(result), thread_num)):
    #     def getCourseOutline(key):
    #         global result
    #         courseId = result[key]['cos_id']
    #         response = nycuTimeTableCrawler.getOutline(courseId)
    #         outline = "" if not response else response["crs_outline"]
    #         result[key]['crs_outline'] = outline
    #     threads = []
    #     end_idx = min(thread_num, len(result) - i)
    #     for j in range(0, end_idx):
    #         thread = threading.Thread(target=getCourseOutline, args=(i + j,))
    #         thread.start()
    #         threads.append(thread)
    #     for thread in threads:
    #         thread.join()
    print(f"Get courses outline")
    result = crawl_outlines(nycuTimeTableCrawler, result)

    file_name = f"{nycuTimeTableCrawler.acysem}.json"
    with open(file_name, "w", encoding="utf8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

crawl_all_course(115, 1)
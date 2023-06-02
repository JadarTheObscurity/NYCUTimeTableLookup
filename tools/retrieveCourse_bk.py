import requests
import json

# A function that sent http post request given the url, header and  data-form
def sent(url,param, data):
    headers = requests.utils.default_headers()
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) ' \
                            'AppleWebKit/537.11 (KHTML, like Gecko) ' \
                            'Chrome/23.0.1271.64 Safari/537.11'
    r = requests.post(url, headers=headers, params=param, data=data)
    return r

def getCourseList(timeTableUrl,departmentId):
    formData = {}
    formData["m_acy"] = 112
    formData["m_sem"] = 1
    formData["m_acyend"] = 112
    formData["m_semend"] = 1
    formData["m_dep_uid"] = departmentId
    formData["m_group"] = "**"
    formData["m_grade"] = "**"
    formData["m_class"] = "**"
    formData["m_option"] = "**"
    formData["m_crsname"] = "**"
    formData["m_teaname"] = "**"
    formData["m_cos_id"] = "**"
    formData["m_cos_code"] = "**"
    formData["m_crstime"] = "**"
    formData["m_crsoutline"] = "**"
    formData["m_costype"] = "**"
    formData["m_selcampus"] = "**"
    return sent(timeTableUrl, {'r': 'main/get_cos_list'}, formData).json()

def saveCourses(courses, coursePath, coursesWithPath):
    """
    {
        "courseId": {
            "dep_id": "xxx",
            "dep_cname": "xxx",
            "dep_ename": "xxx",
            "1" : {
                "1121_562000": {
                    "acy": "112",
                    "sem": "1",
                    "cos_id": "562000",
                    "cos_code": "GELT00001",
                    "num_limit": "25",
                    "dep_limit": "*",
                    "URL": "",
                    "cos_cname": "英文聽力與討論",
                    "cos_credit": "2.00",
                    "cos_hours": "2.00",
                    "TURL": "",
                    "teacher": "楊芳盈",
                    "cos_time": "M34-A405[GF]",
                    "memo": "",
                    "cos_ename": "English Listening and Discussion",
                    "brief": "",
                    "degree": "1",
                    "dep_id": "OU6",
                    "dep_primary": "1",
                    "dep_cname": "語言教學與研究中心",
                    "dep_ename": "Language Teaching and Research Center",
                    "cos_type": "語言溝通",
                    "cos_type_e": "Language & communication",
                    "crsoutline_type": "data",
                    "reg_num": "0",
                    "depType": "O"
                },
            },
            "costype": {},
            "brief": {},
            "language": {}


    }
    """
    for courseListId, courseListInfo in courses.items():
        del courseListInfo['dep_cname']
        del courseListInfo['dep_ename']
        del courseListInfo['dep_id']
        del courseListInfo['language']
        del courseListInfo['costype']
        del courseListInfo['brief']
        # Iterate through the categories
        for key in courseListInfo:
            for courseId, courseInfo in courseListInfo[key].items():
                courseId = courseInfo['cos_id']
                courseSemester = courseInfo['acy'] + courseInfo['sem']
                courseName = courseInfo['cos_cname']
                courseTeacher = courseInfo['teacher']
                courseTime = courseInfo['cos_time']
                coursesWithPath[courseId] = {
                    "courseName": courseName,
                    "courseSemester": courseSemester,
                    "courseTeacher": courseTeacher,
                    "courseTime": courseTime,
                    "coursePath": coursePath
                }
    # del courses[departmentId]['dep_cname']
    # del courses[departmentId]['dep_ename']
    # del courses[departmentId]['dep_id']
    # del courses[departmentId]['language']
    # del courses[departmentId]['costype']
    # del courses[departmentId]['brief']
    # # Iterate through the categories
    # for key in courses[departmentId]:
    #     for courseId, courseInfo in courses[departmentId][key].items():
    #         courseId = courseInfo['cos_id']
    #         courseSemester = courseInfo['acy'] + courseInfo['sem']
    #         courseName = courseInfo['cos_cname']
    #         courseTeacher = courseInfo['teacher']
    #         courseTime = courseInfo['cos_time']
    #         coursesWithPath[courseId] = {
    #             "courseName": courseName,
    #             "courseSemester": courseSemester,
    #             "courseTeacher": courseTeacher,
    #             "courseTime": courseTime,
    #             "coursePath": coursePath
    #         }


timeTableUrl = "https://timetable.nycu.edu.tw/"

semesterStart = 1121
semesterEnd = 1121

paramDefault = {"flang": "zh-tw", "acysem": semesterStart, "acysemend": semesterEnd}
fType = sent(timeTableUrl, {'r': 'main/get_type'}, paramDefault).json()
skipDepList = ["870A5373-5B3A-415A-AF8F-BB01B733444F", "D8E6F0E8-126D-4C2F-A0AC-F9A96A5F6D5D", "E1263D9C-3210-4270-A3FA-FE9A4D283A69", "94EAAC09-C3BC-4BEB-BB9B-47E6F5F652C8", "F01A903B-5DCB-4D88-A24D-EEADA61295AE", "166F5FE8-E532-4D97-9DA7-A28D34D9D88A"]
coursesWithPath = {}
for type in fType:
    depId = type['uid']
    depName = type['cname']
    if depId in skipDepList:
        continue
    print(f"dep: {depId} {depName}")

    paramGetCategory = paramDefault.copy()
    paramGetCategory["ftype"] = depId
    categories = sent(timeTableUrl, {'r': 'main/get_category'}, paramGetCategory).json()
    # 學分學程 的 category 是空的
    if depId == "F01A903B-5DCB-4D88-A24D-EEADA61295AE":
        categories = {"3*": ""}
    # 跨域學程 的 category 是空的
    if depId == "166F5FE8-E532-4D97-9DA7-A28D34D9D88A":
        categories = {"2*": ""}
    # if depId == "FA43258F-8B63-4BA5-BC81-F761371BFD03":
    #     courses = getCourseList(timeTableUrl, depId)
    #     coursePath = f"{depName}"
    #     print(coursePath)
    #     # saveCourses(courses, coursePath, coursesWithPath)
    #     with open(f"./tmp/{coursePath}.json", "w", encoding='utf-8') as f:
    #         json.dump(courses, f,ensure_ascii=False, indent=4)
    #     continue

    print(f"Categories: {categories}")
    for categoryId, categoryName in categories.items():
        print(categoryId, categoryName)
        if depId == "94EAAC09-C3BC-4BEB-BB9B-47E6F5F652C8" or depId == "FA43258F-8B63-4BA5-BC81-F761371BFD03":
            courses = getCourseList(timeTableUrl, categoryId)
            coursePath = f"{depName}_{categoryName}"
            print(coursePath)
            # saveCourses(courses, coursePath, coursesWithPath)
            with open(f"./tmp/{coursePath}.json", "w", encoding='utf-8') as f:
                json.dump(courses, f,ensure_ascii=False, indent=4)
            continue
        paramGetCollege = paramGetCategory.copy()
        paramGetCollege["fcategory"] = categoryId
        colleges = sent(timeTableUrl, {'r': 'main/get_college'}, paramGetCollege).json()
        for collegeId, collegeName in colleges.items():
            print(collegeId, collegeName)
            paramGetDepartment = paramGetCollege.copy()
            paramGetDepartment["fcollege"] = collegeId
            print(f"paramsGetDepartment: {paramGetDepartment}")
            departments = sent(timeTableUrl, {'r': 'main/get_dep'}, paramGetDepartment).json()
            print(f"Departments: {departments}")
            for departmentId, departmentName in departments.items():
                formData = {}
                formData["m_acy"] = 112
                formData["m_sem"] = 1
                formData["m_acyend"] = 112
                formData["m_semend"] = 1
                formData["m_dep_uid"] = departmentId
                formData["m_group"] = "**"
                formData["m_grade"] = "**"
                formData["m_class"] = "**"
                formData["m_option"] = "**"
                formData["m_crsname"] = "**"
                formData["m_teaname"] = "**"
                formData["m_cos_id"] = "**"
                formData["m_cos_code"] = "**"
                formData["m_crstime"] = "**"
                formData["m_crsoutline"] = "**"
                formData["m_costype"] = "**"
                formData["m_selcampus"] = "**"
                courses = sent(timeTableUrl, {'r': 'main/get_cos_list'}, formData).json()
                # print(f"Courses: {courses}")
                coursePath = f"{depName}_{categoryName}_{collegeName}_{departmentName}"
                print(coursePath)
                print(f"departmentId: {departmentId}")
                # saveCourses(courses, coursePath, coursesWithPath)
                with open(f"./tmp/{coursePath}.json", "w", encoding='utf-8') as f:
                    json.dump(courses, f,ensure_ascii=False, indent=4)

                # print(coursePath)
                # saveCourses(courses, coursePath, coursesWithPath)
                # Delete unnecessary information
                # del courses[departmentId]['dep_cname']
                # del courses[departmentId]['dep_ename']
                # del courses[departmentId]['dep_id']
                # del courses[departmentId]['language']
                # del courses[departmentId]['costype']
                # del courses[departmentId]['brief']
                # # Iterate through the categories
                # for key in courses[departmentId]:
                #     for courseId, courseInfo in courses[departmentId][key].items():
                #         courseId = courseInfo['cos_id']
                #         courseSemester = courseInfo['acy'] + courseInfo['sem']
                #         courseName = courseInfo['cos_cname']
                #         courseTeacher = courseInfo['teacher']
                #         courseTime = courseInfo['cos_time']
                #         coursePath = f"{depName}/{categoryName}/{collegeName}/{departmentName}"
                #         coursesWithPath[courseId] = {
                #             "courseName": courseName,
                #             "courseSemester": courseSemester,
                #             "courseTeacher": courseTeacher,
                #             "courseTime": courseTime,
                #             "coursePath": coursePath
                #         }

# Get current time in yyyy-mm-dd hh-mm-ss format
with open(f"results.json", "w", encoding='utf-8') as f:
    json.dump(coursesWithPath, f,ensure_ascii=False, indent=4)

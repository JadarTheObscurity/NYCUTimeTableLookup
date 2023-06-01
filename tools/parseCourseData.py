import json
import os

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
    if not courses:
        print(f"Error: {coursePath} is empty")
        return None
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
                courseIndex = f"{courseId}_{courseName}"
                coursesWithPath[courseId] = {
                    "courseId": courseId,
                    "courseName": courseName,
                    "courseSemester": courseSemester,
                    "courseTeacher": courseTeacher,
                    "courseTime": courseTime,
                    "coursePath": coursePath
                }
courseWithPath = {}
# Print all the file name in the tmp folder
loopCounter = 0
for file in os.listdir("../tmp"):
    print(file)
    with open("../tmp/" + file, "r") as f:
        courses = json.load(f)
        coursePath = file.split(".")[0]
        saveCourses(courses, coursePath, courseWithPath)
    loopCounter += 1

with open("result.json", "w") as f:
    #Turn dictionary to list
    courseWithPathList = list(courseWithPath.values())
    json.dump(courseWithPathList, f, indent=4, ensure_ascii=False, sort_keys=True)
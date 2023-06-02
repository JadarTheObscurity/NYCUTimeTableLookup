import requests
import json

class NYCUTimeTableCrawler:

    def __init__(self, acy:int, sem:int, acyend:int, semend:int):
        self.timeTableUrl = "https://timetable.nycu.edu.tw/"
        self.acy = str(acy)
        self.sem = str(sem)
        self.acyend = str(acyend)
        self.semend = (semend)
        self.acysem = f"{self.acy}{self.sem}"
        self.acysemend = f"{self.acyend}{self.semend}"
        self.paramDefault = {
            "flang": "zh-tw",
            "acysem": self.acysem, 
            "acysemend": self.acysemend,
            "ftype": "*",
            "fcategory": "*",
            "fcollege": "*",
            }

    def saveDepartmentIdAndPath(self, savePath):
        self.allParams = []
        self.getType()
        with open(savePath, "w") as f:
            json.dump(self.allParams, f, ensure_ascii=False, indent=4)

    # A function that sent http post request given the url, header and  data-form
    def sent(self, param, data):
        headers = requests.utils.default_headers()
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) ' \
                                'AppleWebKit/537.11 (KHTML, like Gecko) ' \
                                'Chrome/23.0.1271.64 Safari/537.11'
        r = requests.post(self.timeTableUrl, headers=headers, params=param, data=data)
        return r

    def getCourseList(self, departmentId):
        formData = {}
        formData["m_acy"] = self.acy
        formData["m_sem"] = self.sem
        formData["m_acyend"] = self.acyend
        formData["m_semend"] = self.semend
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
        return self.sent({'r': 'main/get_cos_list'}, formData).json()
    
    def getType(self):
        types = self.sent({'r': 'main/get_type'}, self.paramDefault).json()
        for type in types:
            depId = type['uid']
            depName = type['cname']
            paramGetCategory = self.paramDefault.copy()
            paramGetCategory["ftype"] = depId
            self.getCategory(paramGetCategory, f"{depName}")


    def getCategory(self, params, path:str):
        categories =  self.sent({'r': 'main/get_category'}, params).json()
        for categoryId, categoryName in categories.items():
            paramGetCollege = params.copy()
            paramGetCollege["fcategory"] = categoryId
            # print(f"category: {categoryId} {categoryName}")
            if params["ftype"] in ["870A5373-5B3A-415A-AF8F-BB01B733444F", "D8E6F0E8-126D-4C2F-A0AC-F9A96A5F6D5D"]:
                self.getCollege(paramGetCollege, f"{path}_{categoryName}")
            else:
                self.getDepartment(paramGetCollege, f"{path}{'_'+categoryName if categoryName else ''}")

        

    def getCollege(self, params, path:str):
        colleges =  self.sent({'r': 'main/get_college'}, params).json()
        for collegeId, collegeName in colleges.items():
            # print(f"college: {collegeId} {collegeName}")
            paramGetDepartment = params.copy()
            paramGetDepartment["fcollege"] = collegeId
            self.getDepartment(paramGetDepartment, f"{path}{'_'+collegeName if collegeName else ''}")

    def getDepartment(self, params, path:str):
        departments = self.sent({'r': 'main/get_dep'}, params).json()
        # print(f"dapartment: {departments}")
        for departmentId, departmentName in departments.items():
            departmentPath = f"{path}_{departmentName}"
            print(departmentPath)
            self.allParams.append({"departmentPath": departmentPath, "departmentId": departmentId})

import requests
import json
import aiohttp

class NYCUTimeTableCrawler:

    def __init__(self, acy:int, sem:int):
        self.timeTableUrl = "https://timetable.nycu.edu.tw/"
        self.acy = str(acy)
        self.sem = str(sem)
        self.acyend = str(acy)
        self.semend = (sem)
        self.acysem = f"{self.acy}{self.sem}"
        self.acysemend = f"{self.acyend}{self.semend}"
        self.allDepartments = []
        self.paramDefault = {
            "flang": "zh-tw",
            "acysem": self.acysem, 
            "acysemend": self.acysemend,
            "ftype": "*",
            "fcategory": "*",
            "fcollege": "*",
            }

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
    
    def getOutline(self, courseId):
        formData = {}
        formData["acy"] = self.acy
        formData["sem"] = self.sem
        formData["cos_id"] = courseId
        return self.sent({'r': 'main/getCrsOutlineDescription'}, formData).json()

    def getDepartmentIdAndPath(self):
        self.dept_params_path = []
        self._getType() # Get all the parameters to sent http request and store in self.dept_params_path
        self.allDepartmentsResult = [[] for _ in range(len(self.dept_params_path))] # The list to store response from multi threading http request

        def getDeptId(idx):
            params, path = self.dept_params_path[idx]
            departments = self.sent({'r': 'main/get_dep'}, params).json()
            # print(f"dapartment: {departments}")
            for departmentId, departmentName in departments.items():
                departmentPath = f"{path}_{departmentName}"
                self.allDepartmentsResult[idx].append({"departmentPath": departmentPath, "departmentId": departmentId})

        import threading
        from tqdm import tqdm
        threads = []
        for i in range(0, len(self.dept_params_path)):
            thread = threading.Thread(target=getDeptId, args=(i,))
            thread.start()
            threads.append(thread)
        # Wait for all threads to finish
        for thread in tqdm(threads):
            thread.join()
        self.allDepartments = [r for dept in self.allDepartmentsResult for r in dept]
        return self.allDepartments

        # savePath = f"{self.acysem}_departments.json"
        # with open(savePath, "w", encoding="utf8") as f:
        #     json.dump(self.allDepartments, f, ensure_ascii=False, indent=4)
    
    def _getType(self):
        types = self.sent({'r': 'main/get_type'}, self.paramDefault).json()
        for type in types:
            depId = type['uid']
            depName = type['cname']
            paramGetCategory = self.paramDefault.copy()
            paramGetCategory["ftype"] = depId
            self._getCategory(paramGetCategory, f"{depName}")


    def _getCategory(self, params, path:str):
        categories =  self.sent({'r': 'main/get_category'}, params).json()
        for categoryId, categoryName in categories.items():
            paramGetCollege = params.copy()
            paramGetCollege["fcategory"] = categoryId
            # print(f"category: {categoryId} {categoryName}")
            if params["ftype"] in ["870A5373-5B3A-415A-AF8F-BB01B733444F", "D8E6F0E8-126D-4C2F-A0AC-F9A96A5F6D5D"]:
                self._getCollege(paramGetCollege, f"{path}_{categoryName}")
            else:
                self._getDepartment(paramGetCollege, f"{path}{'_'+categoryName if categoryName else ''}")

    def _getCollege(self, params, path:str):
        colleges =  self.sent({'r': 'main/get_college'}, params).json()
        for collegeId, collegeName in colleges.items():
            # print(f"college: {collegeId} {collegeName}")
            paramGetDepartment = params.copy()
            paramGetDepartment["fcollege"] = collegeId
            self._getDepartment(paramGetDepartment, f"{path}{'_'+collegeName if collegeName else ''}")

    def _getDepartment(self, params, path:str):
        """
        Used for gathering http request parameters
        """
        self.dept_params_path.append([params, path])

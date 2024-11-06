import requests
import json

class KakaoMapCollector:
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {
        "Authorization": "Kakaomap api key"  # 실제 발급받은 키로 대체
    }

    def __init__(self, query="영통역", max_results = 105):
        self.query = query
        self.max_results = max_results
        self.results = []
        self.id_counter = 1
        self.total_count = 0  # 전체 검색 결과 개수 저장

    # 검색 결과의 전체 개수를 가져오는 함수
    def get_total_count(self):
        params = {
            "query": self.query,
            "category_group_code": "FD6",  # 음식점 카테고리 코드
            "size": 1  # 최소한의 데이터만 요청
        }
        response = requests.get(self.url, headers=self.headers, params=params)
        self.total_count = response.json().get("meta", {}).get("total_count", 0)
        print(f"전체 검색 결과 개수: {self.total_count}")

    # 데이터를 수집하여 results에 저장하는 함수, 특정 페이지부터 시작 가능
    def fetch_data(self, start_page=1):
        page = start_page

        while len(self.results) < self.max_results and self.id_counter < self.total_count:
            params = {
                "query": self.query,
                "category_group_code": "FD6",  # 음식점 카테고리 코드
                "page": page,
                "size": 15
            }
            response = requests.get(self.url, headers=self.headers, params=params)
            data = response.json()

            # 데이터가 없을 경우 반복 종료
            documents = data.get("documents", [])
            if not documents:
                break

            for document in documents:
                self.results.append({
                    'id': self.id_counter,
                    'place_name': document.get("place_name"),
                    'category_name': document.get("category_name"),
                    'category_group_name': document.get("category_group_name"),
                    'phone': document.get("phone"),
                    'address_name': document.get("address_name"),
                    'road_address_name': document.get("road_address_name"),
                    'x': document.get("x"),
                    'y': document.get("y"),
                    'place_url': document.get("place_url")
                })
                self.id_counter += 1

            # 페이지와 결과 수 업데이트
            page += 1
            if page > (start_page + 2):  # 최대 3페이지까지만 허용
                self.save_to_json("yeongtong_restaurants.json")  # 45개씩 저장
                self.results.clear()  # 저장 후 결과 리스트 초기화
                self.start_page = page
                break
        return page

    # 수집한 데이터를 JSON 파일로 저장하는 함수
    def save_to_json(self, filename="yeongtong_restaurants.json"):
        with open(filename, "a", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
            f.write(",\n")  # 데이터 구분을 위한 구분자 추가

    def run(self):
        """전체 과정 (개수 가져오기 -> 데이터 수집 -> 저장)을 실행하는 함수"""
        self.get_total_count()         # 전체 검색 결과 개수 가져오기
        start_page = 1
        while(len(self.results) < self.max_results and self.id_counter < self.total_count):
            start_page = self.fetch_data(start_page)    # 데이터 수집 (start_page부터 시작)
        if self.results:
            self.save_to_json()  # 남은 데이터가 있으면 저장


# 사용 예시
collector = KakaoMapCollector()
collector.run()

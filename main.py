from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import os

app = Flask(__name__)

@app.route('/discoverDocument', methods=['POST'])
def discoverDocument():
    if request.is_json:
        data = request.get_json()
        input_banks = data["banks"]
        input_doc_types = data["documentTypes"]
        input_quarter = data["quarter"]
        # Process the JSON data here
        print("Received banks data:", input_banks)
        print("Received document type data:", input_doc_types)
        print("Received quarter data:", input_quarter)

        response_data = []
        for bank in input_banks:
            print("Discovering documents for Bank: ", bank["name"])
            driver = webdriver.Chrome()
            driver.get(bank["irurl"])

            for doc_type in input_doc_types:
                print("Checking for Document type: ", doc_type["name"])
                input_q = input_quarter[0]["name"].split(" ")[0]
                print(input_q)
                input_y = input_quarter[0]["name"].split(" ")[1]
                print(input_y)
                search_pattern = input_q[::-1] + input_y[-2:]
                print(search_pattern)

                elements  = driver.find_elements(By.XPATH, "//a[contains(@href, " + input_y + ")]")
                doc_find_status = "not_found"
                doc_name = ""
                doc_link = ""
                for e in elements:
                    etext = e.get_attribute("text")
                    if (search_pattern in etext) and (doc_type["name"] in etext):
                        doc_find_status = "found"
                        doc_name = e.get_attribute("text")
                        doc_link = e.get_attribute("href")
                        break

                response_data.append({"id": bank["id"] + "-" + doc_type["id"] + "-" + input_quarter[0]["id"], 
                                "bankid": bank["id"],
                                "docType": doc_type["id"],
                                "name": doc_name,
                                "url": doc_link,
                                "status": doc_find_status
                                    })
            driver.quit()

        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@app.route('/downloadDocuments', methods=['POST'])
def downloadDocuments():
    if request.is_json:
        data = request.get_json()
        print("Json received: ",data)
        response_data = []
        for item in data:
            input_id = item["id"]
            input_bankId = item["bankId"]
            input_doc_type = item["docType"]
            input_doc_name = item["name"]
            input_url = item["url"]
            input_status = item["status"]
            input_quarter = item["quarter"]
            
            if input_status == "found":
                response = requests.get(input_url)
                filepath = "Data\\" + input_id.split("-")[0] + "\\" + input_id.split("-")[1] + "\\" + input_id.split("-")[2] + "\\" + input_id + ".pdf"

                directory = os.path.dirname(filepath)
                if directory:
                    os.makedirs(directory, exist_ok=True)

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                response_data.append({"id": input_id, 
                                "bankid": input_bankId,
                                "docType": input_doc_type,
                                "name":input_doc_name,
                                "url": input_url,
                                "status": "downloaded",
                                "quarter": input_quarter
                                    })
        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
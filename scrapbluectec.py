from time import sleep
from selenium import webdriver

def scrapLoadedCTECPage(driver):
    def removeElements(text):
        return text.replace("\n", " ").replace(",", ".").replace("  ", " ");

    classProperties = {
        "url": driver.current_url
    }

    while len(driver.find_elements_by_tag_name("table")) < 2:
        sleep(0.15);

    for element in driver.find_elements_by_tag_name("span"):
        text = element.text;
        if "Student Report for  " in text:
            textSplit = text.split("(",1);
            classProperties["name"] = textSplit[1][1:-1].replace(",", "|");
            classProperties["instructor"] = textSplit[0][len("Student Report for  "):];
        elif "Course and Teacher Evaluations CTEC " in text:
            classProperties["term"] = text[len("Course and Teacher Evaluations CTEC "):];
        elif "_lblSubjectName" in element.get_attribute("id"):
            classProperties["term"] = text.split("Course and Teacher Evaluations CTEC ")[1];
        elif "_lblResponded" in element.get_attribute("id"):
            classProperties["responded"] = text;
        elif "_lblRespRateValue" in element.get_attribute("id"):
            classProperties["respondedRate"] = text;

    for element in driver.find_elements_by_tag_name("table"):
        title = element.get_attribute("summary");
        ratingScript =  """ return document.getElementById('"""  + element.get_attribute("id") + """').querySelector('td[headers="statValueID Mean"]').innerHTML; """;
        if "Provide an overall rating of the instruction" in title:
            classProperties["ratingInstruction"] = driver.execute_script(ratingScript);
        elif "Provide an overall rating of the course." in title:
            classProperties["ratingCourse"] = driver.execute_script(ratingScript);
        elif "Estimate how much you learned in the course." in title:
            classProperties["ratingLearned"] = driver.execute_script(ratingScript);
        elif "Rate the effectiveness of the course in challenging you intellectually." in title:
            classProperties["ratingChallenging"] = driver.execute_script(ratingScript);
        elif "Rate the effectiveness of the instructor in stimulating your interest in the subject." in title:
            classProperties["ratingInterest"] = driver.execute_script(ratingScript);


    for key in classProperties:
        classProperties[key] = removeElements(classProperties[key]);

    return classProperties

def scrapCTECPage(driver, url):
    driver.get(url);

    classTitle = "";
    while len(classTitle) == 0:
        elements = driver.find_elements_by_class_name("coverPageTitleBlock")
        if len(elements) > 0:
            classTitle = elements[0].get_attribute("innerText");
        else:
            sleep(0.5);

    scrapLoadedCTECPage(driver);

import urllib2
import argparse

from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from authcaesar import authenticate
from scrapbluectec import scrapLoadedCTECPage
from dicttocsv import saveDictionariesToCSV

def wait(driver, elementID, delay):
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, elementID)))
        return myElem
    except TimeoutException:
        print "Loading took too much time!"

def fetchSubjectCTECs(driver, subject):
    print("=============")

    print("Main Page -> Go to Student Page")
    mainPageManageClassesButton = wait(driver, 'PTNUI_LAND_WRK_GROUPBOX14$PIMG', 15)
    mainPageManageClassesButton.click();
    sleep(2);
    mainPageManageClassesButton = wait(driver, 'PTNUI_SELLP_DVW_PTNUI_LP_NAME$span$1', 15)
    mainPageManageClassesButton.click();
    sleep(2);

    print("Main Page -> Click Manage Classes")
    mainPageManageClassesButton = wait(driver, 'win0divPTNUI_LAND_REC_GROUPLET$8', 15)
    mainPageManageClassesButton.click();
    sleep(2);

    print("Manage Classes Page -> Click Search CTECs")
    classesPageCTECRow = wait(driver, 'PT_SIDE$tab', 15)
    sleep(1);
    classesPageCTECRow.click();

    classesPageCTECRow = wait(driver, 'win12divPTGP_STEP_DVW_PTGP_STEP_LABEL$7', 15)
    sleep(1);
    classesPageCTECRow.click();

    print("- Waiting for careers to load")
    delay = 15;
    try:
        careerSelectorDropdown = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#NW_CT_PB_SRCH_ACAD_CAREER')))
    except TimeoutException:
        print "Loading took too much time!"

    driver.execute_script("document.querySelector('#NW_CT_PB_SRCH_ACAD_CAREER').value = 'UGRD'");
    driver.execute_script("document.querySelector('#NW_CT_PB_SRCH_ACAD_CAREER').onchange();");

    print("- Waiting for subjects to load")
    sleep(0.25);
    while driver.execute_script("return document.getElementById('processing').offsetParent == null") == False:
        sleep(0.5);

    subjectSelectorDropdown = driver.find_element_by_css_selector("#NW_CT_PB_SRCH_SUBJECT");
    options = driver.find_elements_by_tag_name("option");
    validClass = False;

    for option in options:
        if (option.get_attribute('value') == subject):
            validClass = True;

    if (validClass):
        print("- Found correct class subject")
        driver.execute_script("document.querySelector('#NW_CT_PB_SRCH_SUBJECT').value = '" + subject + "'");
        driver.execute_script("document.querySelector('#NW_CT_PB_SRCH_SUBJECT').onchange();");
    else:
        driver.quit();
        raise ValueError("Couldn't find subject")

    sleep(1);
    print("- Waiting for single class results to load")
    driver.execute_script("document.getElementById('NW_CT_PB_SRCH_SRCH_BTN').click();");

    # One off to get past main screen
    try:
        classesPageCTECResultRow = [];
        checkCount = 0;
        while len(classesPageCTECResultRow) == 0:
            checkCount = checkCount + 1;
            links = driver.find_elements_by_class_name("psc_rowact");
            for link in links:
                if "NW_CT_PV_DRV$0_row_" in link.get_attribute('id'):
                    classesPageCTECResultRow.append(link);
                    break;
            sleep(0.25)
            if checkCount > 60:
                print("- Something unexpected happened, skipping subject")
                return;
    except:
        print("- Something unexpected happened, skipping subject")
        return;

    print("Manage Classes Page / CTEC Section -> Click CTEC Result")
    driver.find_element_by_id(classesPageCTECResultRow[0].get_attribute('id')).click()
    wait(driver, 'NW_CT_PV4_DRV$0_row_0', 30)

    # Now viewing full ctec view (classes on left, section reviews table on right)
    fullCTECPageClassList = [];
    while len(fullCTECPageClassList) == 0:
        links = driver.find_elements_by_class_name("psc_rowact");
        for link in links:
            if "NW_CT_PV_DRV$0_row_" in link.get_attribute('id'):
                fullCTECPageClassList.append(link);
        sleep(0.25)

    print("-------------")
    print("Found " + str(len(fullCTECPageClassList)) + " classes in sidebar");
    print("Starting CTEC Scrap")

    main_window = driver.current_window_handle;
    scrappedCTECs = [];

    scrappedClasses = 0;

    lastFirstResultClassDes = "";
    for classRow in fullCTECPageClassList:

        try:
            scrappedClasses += 1;

            driver.execute_script("document.getElementById('" + classRow.get_attribute('id') + "').click();")

            classNumber = classRow.get_attribute('innerText').split('-')[0];
            resultsLoaded = False;
            waitCount = 0;

            while resultsLoaded == False and waitCount < 30:
                firstResultDes = driver.find_element_by_id("MYDESCR$0").get_attribute('innerText');
                if lastFirstResultClassDes is not firstResultDes:
                    resultsLoaded = True;
                    lastFirstResultClassDes = firstResultDes;
                else:
                    waitCount = waitCount + 1;
                    sleep(0.5);

            if waitCount == 30:
                print("- " + str(classNumber) + ": Results appear the same, skipping");
                continue;

            print("- " + str(classNumber) + ": Starting")

            classCTECRow = [];
            links = driver.find_elements_by_class_name("psc_rowact");
            for link in links:
                if "NW_CT_PV4_DRV$0_row_" in link.get_attribute('id'):
                    classCTECRow.append(link);

            print("- " + str(classNumber) + ": Waiting 5S For Load")
            sleep(5);
            scrappedRows = 0;
            onlyOldResultsLeft = False;

            for resultRow in classCTECRow:
                sleep(0.2);
                if onlyOldResultsLeft:
                    break;

                scrappedRows += 1;
                name = driver.find_element_by_id("MYDESCR$" + str(scrappedRows - 1)).get_attribute("innerText");
                driver.execute_script("document.getElementById('" + resultRow.get_attribute('id') + "').click();")

                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) == 2)

                onCTECTab = False;
                validBluePage = False;

                while onCTECTab == False:
                    for handle in driver.window_handles:
                        driver.switch_to.window(handle)
                        sleep(0.1)
                        if "Northwestern - " in driver.title:
                            onCTECTab = True;
                            validBluePage = True;
                            break;
                        elif "NU:" in driver.title:
                            onCTECTab = True;
                            validBluePage = False;
                            break;
                        elif "NU CTEC Published Reports" in driver.title:
                            if handle != main_window:
                                onCTECTab = True;
                                validBluePage = False;
                                onlyOldResultsLeft = True;
                                break;

                if validBluePage:
                    delay = 30;
                    try:
                        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'reportView')))
                    except TimeoutException:
                        print "Loading took too much time!"

                    scrap = scrapLoadedCTECPage(driver);
                    scrap["shortName"] = name.replace(",", "|");
                    scrappedCTECs.append(scrap);
                    print("-- Progress: " + str(scrappedRows) + "/" + str(len(classCTECRow)))
                elif onlyOldResultsLeft:
                    print("- " + str(classNumber) + ": Only old CTECs left, skipping the rest")
                else:
                    print("-- Invalid CTEC Page")
                    print("-- Progress: " + str(scrappedRows) + "/" + str(len(classCTECRow)))

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            print("- Overall Progress: " + str(scrappedClasses) + "/" + str(len(fullCTECPageClassList)))
        except Exception as e:
            print("- " + str(classNumber) + ": Something unexpected happened, skipping class")
            continue;

    saveDictionariesToCSV(scrappedCTECs, subject + "-CTECs");


if __name__ == "__main__":

    # Arg Parse
    parser = argparse.ArgumentParser();
    parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("-m", "--Mode", type=str, help='Script Mode. "Class" = Class Fetch, "Subject" = Subject Fetch.');

    required.add_argument("-n", "--NetID", type=str);
    required.add_argument("-p", "--Password", type=str);

    optional.add_argument("-s", '--Subjects', type=str, help='Subjects in Caesar. Case-sensitive, comma seperated (i.e. "MATH,CHEM")');
    optional.add_argument("-as", "--All_Subjects", action='store_true', help='Scrap all subjects in caesar.');

    optional.add_argument("-t", "--Term", type=str, help='Class term. Only valid for class fetch mode. Case-sensitive (i.e. Fall 2017)');
    optional.add_argument("-i", "--ClassID", type=str, help='Class ID term. Only valid for class fetch mode (i.e. 230)');

    args = parser.parse_args();

    if args.Mode is None:
        raise ValueError("Script mode requried.")
    elif args.Mode != "Class" and args.Mode != "Subject":
        raise ValueError("Invalid mode.")
    elif args.NetID is None:
        raise ValueError("NetID requried.")
    elif args.Password is None:
        raise ValueError("Password requried.")
    elif args.Mode == "Class":
        if args.Term is None:
            raise ValueError("Term requried.")
        elif args.ClassID is None:
            raise ValueError("Class ID requried.")


    if args.Mode == "C":
        print("Class fetch is currently broken (Built for old Caesar)")
        # fetchClassData(driver, args.Term, args.Subject, args.ClassID)
    else:
        subjects = [];
        if args.All_Subjects is not None:
            subjects = ["AAL","AFST","AF_AM_ST","ALT_CERT","AMER_ST","AMES","ANIM_ART","ANTHRO","ARABIC","ART","ART_HIST","ASIAN_AM","ASIAN_LC","ASIAN_ST","ASTRON","BIOL_SCI","BMD_ENG","BUS_INST","CAT","CFS","CHEM","CHEM_ENG","CHINESE","CHRCH_MU","CIV_ENG","CIV_ENV","CLASSICS","CMN","COG_SCI","COMM_SCI","COMM_ST","COMP_LIT","COMP_SCI","CONDUCT","COOP","CRDV","CSD","DANCE","DSGN","EARTH","ECE","ECON","EDIT","EECS","ENGLISH","ENTREP","ENVR_POL","ENVR_SCI","ES_APPM","EUR_ST","EUR_TH","FRENCH","GBL_HLTH","GEN_CMN","GEN_ENG","GEN_LA","GEN_MUS","GEN_SPCH","GEOG","GEOL_SCI","GERMAN","GNDR_ST","GREEK","HDPS","HEBREW","HINDI","HIND_URD","HISTORY","HUM","IDEA","IEMS","IMC","INTG_ART","INTG_SCI","INTL_ST","ISEN","ITALIAN","JAPANESE","JAZZ_ST","JOUR","JWSH_ST","KELLG_FE","KELLG_MA","KOREAN","LATIN","LATINO","LATIN_AM","LDRSHP","LEGAL_ST","LING","LOC","LRN_DIS","MATH","MAT_SCI","MECH_ENG","MENA","MFG_ENG","MMSS","MUSIC","MUSICOL","MUSIC_ED","MUS_COMP","MUS_TECH","MUS_THRY","NEUROSCI","PERF_ST","PERSIAN","PHIL","PHYSICS","PIANO","POLI_SCI","PORT","PRDV","PSYCH","RELIGION","RTVF","SESP","SHC","SLAVIC","SOCIOL","SOC_POL","SPANISH","SPCH","STAT","STRINGS","SWAHILI","TEACH_ED","THEATRE","TRANS","TURKISH","URBAN_ST","VOICE","WIND_PER","WM_ST","WRITING","YIDDISH'"];
        elif args.Subjects is not None:
            subjects = args.Subjects.split(',');
        else:
            raise ValueError("Must specify -s or -as in Subject Fetch");

        # Driver
        driver = webdriver.Safari();

        # Authenticate
        authenticate(driver, args.NetID, args.Password);

        for subject in subjects:
            try:
                url = "https://caesar.ent.northwestern.edu/";
                driver.get(url)
                sleep(5);
                fetchSubjectCTECs(driver, subject);
            except:
                print(subject + ": Something unexpected happened, skipping subject")

    driver.quit();

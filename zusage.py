import win32com.client
import sys
import os
import time
import shutil
import datetime

def saplogin(sysID,clNo,usrID,pwRd, dwnPath):
    '''
        This function will Login to SAP from the SAP Logon window                    
    '''

    print("***** Please enter date on next input *****")
    print("***** For todays date press enter *****")
    start_date = input("Enter start date ex: dd.mm.yyyy: ")
    end_date = input("Enter end date ex: dd.mm.yyyy: ")
    total_days = int(input("Enter total no of days: ") or 1)
    
    application = win32com.client.Dispatch("Sapgui.ScriptingCtrl.1")
    connection = application.Openconnection(sysID,True)
    session = connection.Children(0)
    
    ######## Code For Login into SAP System #######
    session.findById("wnd[0]/usr/txtRSYST-MANDT").text = clNo
    session.findById("wnd[0]/usr/txtRSYST-BNAME").text = usrID
    session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = pwRd
    session.findById("wnd[0]").sendVKey(0)

    ######### Steps to execute tcode SM37  ############
    dt = datetime.datetime.now()

    # if no user input todays date will be taken 
    if len(start_date) == 0 and len(end_date) == 0:
        start_date = dt.strftime("%d.%m.%Y")
        end_date = dt.strftime("%d.%m.%Y")

    file_path = dwnPath + f"\{start_date.replace('.', '-')}"
            
    # create folder
    if not os.path.exists(file_path):
        os.makedirs(file_path)   

    session.findById("wnd[0]/tbar[0]/okcd").text = "/nsm37"
    session.findById("wnd[0]").sendVKey(0)
 
    if session.findById("wnd[0]/sbar").Text != "You are not authorized to use transaction SM37":
        try:
            session.findById("wnd[0]/usr/txtBTCH2170-JOBNAME").text = "ZUSAGE DAILY PROGRAM"
            session.findById("wnd[0]/usr/txtBTCH2170-USERNAME").text = "*"
            session.findById("wnd[0]/usr/ctxtBTCH2170-FROM_DATE").text = start_date
            session.findById("wnd[0]/usr/ctxtBTCH2170-TO_DATE").text = end_date
            session.findById("wnd[0]/usr/ctxtBTCH2170-TO_DATE").setFocus()
            session.findById("wnd[0]/usr/ctxtBTCH2170-TO_DATE").caretPosition = 10
            session.findById("wnd[0]/tbar[1]/btn[8]").press()

            count = 1
            value = 13
            while (count <= total_days):
                session.findById(f"wnd[0]/usr/lbl[37,{value}]").setFocus()
                session.findById(f"wnd[0]/usr/lbl[37,{value}]").caretPosition = 0
                session.findById("wnd[0]").sendVKey(2)

                # define report date
                report_date, report_day, report_month = '', '', ''

                for i in range(3, 30):
                    file_size = session.findById(f"wnd[0]/usr/lbl[43,{i}]").text

                    if (bool(file_size) == True):
                        session.findById(f"wnd[0]/usr/lbl[54,{i}]").setFocus()
                        file_name = session.findById(f"wnd[0]/usr/lbl[54,{i}]").text
                        session.findById(f"wnd[0]/usr/lbl[54,{i}]").caretPosition = 6
                        session.findById("wnd[0]/tbar[1]/btn[34]").press()
                        session.findById("wnd[0]/usr/lbl[14,3]").setFocus()
                        session.findById("wnd[0]/usr/lbl[14,3]").caretPosition = 0
                        session.findById("wnd[0]").sendVKey(2)

                        if (len(report_date) == 0):
                            report_date = session.findById("wnd[0]/usr/lbl[1,20]").text

                        report_day = session.findById("wnd[0]/usr/lbl[1,20]").text.split('.')[0]
                        session.findById("wnd[0]/tbar[1]/btn[48]").press()
                        session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
                        session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
                        session.findById("wnd[1]/tbar[0]/btn[0]").press()
                        session.findById("wnd[1]/usr/ctxtDY_PATH").text = file_path
                        session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = f"{file_name}_{report_day}.xls"
                        session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 8
                        session.findById("wnd[1]/tbar[0]/btn[0]").press()
                        session.findById("wnd[0]/tbar[0]/btn[3]").press()
                        session.findById("wnd[0]/tbar[0]/btn[3]").press()

                report_date = report_date.split('.')

                # extract month from report date
                report_month = datetime.datetime(
                    int(report_date[2]),
                    int(report_date[1]),
                    int(report_date[0]),
                )

                report_month = report_month.strftime('%b')

                # archiving file
                zip_file_name = dwnPath + f"\ZUSAGE_{report_day}_{report_month}"
                
                shutil.make_archive(
                    zip_file_name.upper(),
                    'zip',
                    file_path)
            
                # removing folder
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                
                count += 1
                value += 1

                session.findById("wnd[0]/tbar[0]/btn[3]").press()

            session.findById("wnd[0]/tbar[0]/okcd").text = "/nex"
            session.findById("wnd[0]").sendVKey(0)
            
            return "Successfully executed SM37 transaction code"
        except Exception as error:
            print(error)
        return "Problem occured while processing SM37 transaction code"
    else:
        return "You are not authorized to use transaction SM37"

if __name__ == "__main__":
    sysID = str(sys.argv[1])
    clNo = str(sys.argv[2])
    usrID = str(sys.argv[3])
    pwRd = str(sys.argv[4])   
    dwnPath  = str(sys.argv[5])
    outputMsg = saplogin(sysID,clNo,usrID,pwRd, dwnPath)   
    print(outputMsg)
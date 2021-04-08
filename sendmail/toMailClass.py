# encoding:GBK
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
from log.loginfo import LogFile
log = LogFile(__name__).getlog()
class Mail(object):
  def __init__(self, host, nickname, username, password, postfix):
    self.host = host
    self.nickname = nickname
    self.username = username
    self.password = password
    self.postfix = postfix
 
  def send_mail(self, to_list, subject, content=[], cc_list=[], encode='gbk', is_html=True, images=[]):
    me = str(Header(self.nickname, encode)) + "<" + self.username + "" + self.postfix + ">"
    msg = MIMEMultipart()
    msg['Subject'] = Header(subject, encode)
    msg['From'] = me
    msg['To'] = ','.join(to_list)
    msg['Cc'] = ','.join(cc_list)
    if is_html:
      msglist_time=[]
      img_temp=[]
      img=''
      #重新组装images数据
      for i in range(len(images)):
        img='<p><img src="cid:image%d"></p>' % (i+1)
        img_temp.append(img)
      #交叉合并content[list]和images[list]变成content
      for i in range(max(len(content), len(img_temp))):
        if content:
          msglist_time.append(content.pop())
        if img_temp:
          msglist_time.append(img_temp.pop())
      mail_msgs =''.join(msglist_time)
      msg.attach(MIMEText(mail_msgs, 'html', 'utf-8'))

 
      for i, img_name in enumerate(images):
        with open(img_name, 'rb') as fp:
          img_data = fp.read()
        msg_image = MIMEImage(img_data)
        msg_image.add_header('Content-ID', '<image%d>' % (i+1))
        msg.attach(msg_image)
        # 将图片作为附件
        # image = MIMEImage(img_data, _subtype='octet-stream')
        # image.add_header('Content-Disposition', 'attachment', filename=images[i])
        # msg.attach(image)
    else:
      msg_content = MIMEText(content, 'plain', encode)
      msg.attach(msg_content)
 
    try:
      s = smtplib.SMTP()
      # s.set_debuglevel(1)
      s.connect(self.host)
      s.login(self.username, self.password)
      s.sendmail(me, to_list + cc_list, msg.as_string())
      s.quit()
      s.close()
      log.info("邮件发送成功")
      return True
    except Exception as e:
      log.error("发送邮件出错："+str())
      print(e)
      return False
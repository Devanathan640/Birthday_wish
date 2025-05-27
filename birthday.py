from datetime import datetime, timedelta,timezone
import time,requests,dotenv,os,pytz,json,yagmail,calendar
from cryptography.fernet import Fernet

dotenv.load_dotenv()

ciper=Fernet(os.getenv('KEY'))
def post_data(name,password):
    headers = {
        "Authorization": "Basic bXktdHJ1c3RlZC1jbGllbnQ6c2VjcmV0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "password",
        f"username": {name},
        f"password": {password}
    }
    url="https://ess.changepond.com/ESS-Java/oauth/token"
    try:
        for i in range(5):
            res=requests.post(url,headers=headers,data=data)
            response=res.json()
            access_token=response.get('access_token')
            if res.status_code==200:
                return access_token
            time.sleep(2)
    except Exception as e:
        print(e)
        print("Data not found")
        return None 
    
def get_details(access_token):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    url=f"https://ess.changepond.com/ESS-Java/api/emplyee/getEmployeeBirthdayDetails/"
    for i in range(5):
        get_data=requests.get(url,headers=headers)
        if get_data.status_code==200:
            break
        time.sleep(2)
    get_response=get_data.json()
    return get_response


def emp_data(datas):
    final=[]
    for data in datas:
        if data['empId']>='4558' and  data['empId']<='4599':
            today=datetime.now().strftime('%Y')
            encoded_dob = data['dob']
            base_epoch = 312319132200000
            actual_ms = encoded_dob - base_epoch
            decoded_date = datetime(1970, 1, 1) + timedelta(milliseconds=actual_ms)
            finl={"emp_id":data['empId'],'name':data['employeeName'],"birthday_date":decoded_date.strftime("%d-%m")+f"-{today}"} 
            final.append(finl)
    final=json.dumps(final)
    with open('b_data.json','w') as bd:
        bd.writelines(final)
    return bd

def encrypt_data(value,key):
    return key.encrypt(value.encode()).decode()

def decrypt_data(value,key):
    return key.decrypt(value.encode()).decode()

def send_email(to_mail,cc,subject,body):
    yag=yagmail.SMTP('devanathan.pain@gmail.com')
    yag.send(to_mail,subject=subject,cc=cc,contents=body)
    return

def pre_whish(data):
    subject=f'🎉 Reminder: Tomorrow is {data}\'s Birthday!'

    email_body=f'''
    Hey everyone,

    Just a quick reminder that tomorrow is our dear friend {data}'s birthday! 🎂🥳
    
    Let’s make it special by sending our wishes, sharing some memories, or even planning a surprise if possible.

    It’s a great chance to show how much we appreciate and care for {data}.

    Feel free to reply if you have any ideas for a small celebration or gift!

    Cheers,
    Changepondians💕
'''
    return subject,email_body

def post_wish(data):
    Subject=f'🎉 Happy Birthday {data["name"]}!'

    body=f'''
    Vanakkam da mapla,

   Indru un special day! Ellarukkagavum naanga ore saththama solla varrom – Pirandha naal vaalthukkal da machi! 🥳🎂

Eppavumadhiri indha varudhamum nee santhoshama irukkanum, un dreams ellam nijamavanum, neraiya cake saapudanum 😄

Namba ellarum serumbodhu dhaan kelikkaiyum santhoshathukkum artham irukkum. Nee eppavum ippadiye sirichikittu irukkanum!

Seekirama celebrate pannalaam – love you da macha! ❤️

– Un kootam muzhuvadhum 😎
    '''

    return Subject,body


def get_data_from_conf():
    with open("b_data.json",'r') as bd:
        data=bd.read()
        data=json.loads(data)
    return data

def send_birthday_wish_today():
    today=datetime.now()
    data=get_data_from_conf()
    cc_list=[decrypt_data(value['mail'],ciper) for value in data if value['mail']]
    to_mail=[]
    data_of_bd=[]
    for value in data:
        b_day=datetime.strptime(value['birthday_date'],'%d-%m-%Y')
        b_day_m=b_day.month
        b_date=b_day.day
        if b_date==today.day and b_day_m==today.month:
            if value['mail']:
                mail=decrypt_data(value['mail'],ciper)
                cc_list.pop(cc_list.index(mail))
                to_mail.append(mail)
                data_of_bd.append(value)
    for val in range(len(data_of_bd)):
        subject,body=post_wish(data_of_bd[val])
        send_email(to_mail[val],cc_list,subject,body)
    return 

def send_email_for_tommorw():
    today=datetime.now()+timedelta(days=1)    
    data=get_data_from_conf()
    cc_list=[decrypt_data(value['mail'],ciper) for value in data if value['mail']]
    tm_bd=[]
    for value in data:
        b_day=datetime.strptime(value['birthday_date'],'%d-%m-%Y')
        b_day_m=b_day.month
        b_date=b_day.day
        print(today.day,today.month)
        if b_date==today.day and b_day_m==today.month:
            if value['mail']:
                mail=decrypt_data(value['mail'],ciper)
                cc_list.pop(cc_list.index(mail))
                tm_bd.append(value['name'])
    print(cc_list)
    if tm_bd:
        subject,body=pre_whish(", ".join(tm_bd))
        send_email(cc_list,cc=None,subject=subject,body=body)

def encrypt_and_decrypyt():
    ciper=Fernet(os.getenv('KEY'))
    with open("b_data.json",'r') as bd:
        data=bd.read()
        data=json.loads(data)
    for value in data:
        if value['mail'] and '@' in value['mail']:  
            value['mail']=encrypt_data(value['mail'],ciper)
    data=json.dumps(data)
    with open("b_data.json",'w') as bd:
        bd.writelines(data)

if __name__=="__main__":
    emp_id="4559"
    pass_word=os.getenv('ESS_PASSWORD')
    # access_token=post_data(emp_id,password=pass_word)
    # data=get_details(access_token)
    # emp_data(data)
    send_birthday_wish_today()
    send_email_for_tommorw()
    # encrypt_and_decrypyt()
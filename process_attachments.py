import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

# 定义不同情况对应的附件要求
requirements = {
    1: ['合同名称及合同', '发票', '完税证明', '情况说明'],
    2: ['股东决议名称及上传', '利润分配计算表', '非居民企业递延纳税信息报告表'],
    3: ['股东决议名称及上传', '利润分配计算表', '被分配利润公司所在国家税收居民证明', '被分配利润公司财务报表', '非居民企业享受协定待遇信息报告表'],
    4: ['股东决议名称及上传', '利润分配计算表'],
    5: ['合同名称及合同', '发票'],  # 需要特殊处理PO号
    6: ['合同名称及合同', '发票'],
    7: ['合同名称及合同', '发票', '情况说明', '服务成果', '沟通邮件'],
    8: ['合同名称及合同', '发票', '情况说明', '委托授权书', '服务人员护照首页及出入境页'],
    9: ['合同名称及合同', '发票', '情况说明', '委托授权书']
}

def main():
    if len(sys.argv) != 5:
        print("Usage: python process_attachments.py <attachments_json> <situation_id> <po_amount> <email>")
        sys.exit(1)

    attachments_json = sys.argv[1]
    situation_id = int(sys.argv[2])
    po_amount = int(sys.argv[3])
    user_email = sys.argv[4]

    with open(attachments_json, 'r') as f:
        attachments = json.load(f)

    # 检查情况ID是否在定义的要求中
    if situation_id not in requirements:
        return {'status': 'error', 'message': '未知的情况ID'}

    required_attachments = requirements[situation_id]
    
    # 特殊处理情况5的PO号
    if situation_id == 5 and po_amount < 50000:
        required_attachments = [attachment for attachment in required_attachments if attachment != '合同名称及合同']

    # 获取所有附件的名称（不包括扩展名）
    attachment_names = [os.path.splitext(att['name'])[0] for att in attachments]
    
    # 检查每个所需附件是否存在至少一个
    missing_attachments = []
    for required_attachment in required_attachments:
        if not any(required_attachment in name for name in attachment_names):
            missing_attachments.append(required_attachment)
    
    # 如果有缺少的附件，发送邮件并返回错误信息
    if missing_attachments:
        send_missing_attachments_email(user_email, missing_attachments)
        return {'status': 'error', 'message': '缺少附件', 'missing_attachments': missing_attachments}
    
    # 如果所有检查都通过，返回成功信息
    return {'status': 'success', 'message': '所有附件均已上传'}

def send_missing_attachments_email(user_email, missing_attachments):
    sender_email = "your-email@example.com"
    sender_password = os.environ.get('EMAIL_PASSWORD')
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "缺少附件通知"
    message["From"] = sender_email
    message["To"] = user_email

    text = f'尊敬的客户，\n\n您提交的资料缺少以下附件：\n' + '\n'.join(missing_attachments) + '\n\n请尽快补充。谢谢！'
    part = MIMEText(text, "plain")
    message.attach(part)

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, message.as_string())

if __name__ == "__main__":
    main()

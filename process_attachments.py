import os
import sys
import shutil

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
    if len(sys.argv) != 4:
        print("Usage: python process_attachments.py <attachments_dir> <situation_id> <po_amount>")
        sys.exit(1)

    attachments_dir = sys.argv[1]
    situation_id = int(sys.argv[2])
    po_amount = int(sys.argv[3])

    print(f"Processing situation_id: {situation_id}, po_amount: {po_amount}")

    # 检查情况ID是否在定义的要求中
    if situation_id not in requirements:
        print(f"Unknown situation ID: {situation_id}")
        clean_up(attachments_dir)
        print('::set-output name=status::0')
        print('::set-output name=missing_attachments::未知的情况ID')
        return

    required_attachments = requirements[situation_id]
    
    # 特殊处理情况5的PO号
    if situation_id == 5 and po_amount < 50000:
        required_attachments = [attachment for attachment in required_attachments if attachment != '合同名称及合同']

    # 获取所有附件的名称（不包括扩展名）
    attachment_names = [os.path.splitext(filename)[0] for filename in os.listdir(attachments_dir)]
    
    # 检查附件
    missing_attachments = []
    for required_attachment in required_attachments:
        if not any(required_attachment in name for name in attachment_names):
            missing_attachments.append(required_attachment)
    
    # 清空 data 文件夹
    clean_up(attachments_dir)

    # 如果有缺少的附件，返回 0 并写入缺少的附件名称
    if missing_attachments:
        print(f"Missing attachments: {missing_attachments}")
        print('::set-output name=status::0')
        print(f"::set-output name=missing_attachments::{', '.join(missing_attachments)}")
        return

    print("All attachments are present.")
    # 如果所有检查都通过，返回 1
    print('::set-output name=status::1')
    print('::set-output name=missing_attachments::')
    return

def clean_up(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

if __name__ == "__main__":
    main()

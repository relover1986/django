#%%
import re

def parse_blasting_input(text, year=2026, debug=False):
    """解析雷管炸药台账文本"""
    lines = text.strip().split('\n')
    
    person = ""
    location = ""
    date = ""
    sum_1_to_6 = 0
    sum_7_up = 0
    label_det = 0
    label_dyn = 0
    shift = ""
    segments = {}
    
    # 检查所有 "N-M各一发" 的模式（通用化：任意 N-M 范围）
    pat_range = re.compile(r'(\d+)[-—](\d+)各一(?:发|个段)')
    range_matches = pat_range.findall(text)
    range_segs_set = set()  # 记录哪些段已被各一发覆盖
    for n_str, m_str in range_matches:
        n, m = int(n_str), int(m_str)
        for s in range(n, m + 1):
            segments[str(s)] = 1
            range_segs_set.add(s)
            if 1 <= s <= 6:
                sum_1_to_6 += 1
            elif s >= 7:
                sum_7_up += 1
    
    # 逐行解析
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # 1. 人员、地点、日期（第一行）
        if not person or not location or not date:
            # 先检查是否包含日期
            has_date = re.search(r'(\d+月\d+[日号])', line)
            
            if has_date:
                # 有日期的情况
                date_str = has_date.group(1).replace('号', '日')
                date = f"{year}年{date_str}"
                
                # 提取日期前的内容
                before_date = line[:has_date.start()].strip()
                
                # 用分隔符分割前半部分
                separators = [' ', '，', ',', '.', '、', '；', ';']
                parts = []
                current = ""
                for char in before_date:
                    if char in separators:
                        if current.strip():
                            parts.append(current.strip())
                        current = ""
                    else:
                        current += char
                if current.strip():
                    parts.append(current.strip())
                
                # 检查第一部分是否为班次
                pat_shift = re.compile(r'^(白|夜|早|中|晚|早班|中班|晚班|白班|夜班)$')
                si = 1 if (parts and pat_shift.match(parts[0])) else 0
                if si:
                    shift = parts[0]
                if len(parts) >= si + 2:
                    person = parts[si]
                    location = parts[si + 1]
                elif len(parts) >= si + 1:
                    person = parts[si]
                    location = ""
            
            else:
                # 没有日期的情况，用分隔符分割
                separators = [' ', '，', ',', '.', '、', '；', ';']
                parts = []
                current = ""
                for char in line:
                    if char in separators:
                        if current.strip():
                            parts.append(current.strip())
                        current = ""
                    else:
                        current += char
                if current.strip():
                    parts.append(current.strip())
                
                # 检查第一部分是否为班次
                pat_shift = re.compile(r'^(白|夜|早|中|晚|早班|中班|晚班|白班|夜班)$')
                si = 1 if (parts and pat_shift.match(parts[0])) else 0
                if si:
                    shift = parts[0]
                if len(parts) >= si + 2:
                    person = parts[si]
                    location = parts[si + 1]
                elif len(parts) >= si + 1:
                    person = parts[si]
                    location = ""
        
        # 2. 段号-数量（跳过已被各一发覆盖的段号行）
        pat_item = re.compile(r'(\d+)[/\-—一](\d+)')
        items = pat_item.findall(line)
        for item in items:
            seg = int(item[0])
            cnt = int(item[1])
            # 仅当该段未被各一发覆盖时才累加
            if seg not in range_segs_set:
                segments[str(seg)] = segments.get(str(seg), 0) + cnt
                if 1 <= seg <= 6:
                    sum_1_to_6 += cnt
            if seg >= 7:
                sum_7_up += cnt
        
        # 3. 雷管
        pat_det = re.compile(r'(?:雷)?管(\d+)发')
        det_matches = pat_det.findall(line)
        if det_matches:
            label_det = int(det_matches[-1])
        
        # 4. 炸药/火药
        pat_dyn = re.compile(r'(?:火)?药(?:料)?(\d+)公斤|(?:炸)?药(\d+)公斤')
        dyn_matches = pat_dyn.findall(line)
        if dyn_matches:
            all_nums = []
            for match in dyn_matches:
                for g in match:
                    if g:
                        all_nums.append(int(g))
            if all_nums:
                label_dyn = all_nums[-1]
    
    calc_det = sum_1_to_6 + sum_7_up
    check_ok = calc_det == label_det
    
    return {
        "班次": shift,
        "人员": person,
        "地点": location,
        "日期": date,
        "1-6段累加": sum_1_to_6,
        "7段以后累加": sum_7_up,
        "计算雷管总数": calc_det,
        "雷管": label_det,
        "炸药": label_dyn,
        "雷管核对": "正确" if check_ok else "不一致",
        "segments": segments
    }


def extract_summary_data(text, year=2026):
    """提取人员、地点、日期、雷管数、炸药数"""
    result = parse_blasting_input(text, year=year, debug=False)
    return {
        "人员": result["人员"],
        "地点": result["地点"],
        "日期": result["日期"],
        "雷管数": result["雷管"],
        "炸药数": result["炸药"]
    }


def summarize_multiple_records(text_list, year=2026):
    """批量汇总多条记录"""
    all_data = []
    
    for i, text in enumerate(text_list, 1):
        try:
            data = extract_summary_data(text, year=year)
            data["序号"] = i
            all_data.append(data)
        except Exception as e:
            print(f"第 {i} 条记录解析失败: {e}")
    
    return all_data


def print_summary_table(data_list):
    """打印汇总表格"""
    print("=" * 90)
    print("雷管炸药台账汇总")
    print("=" * 90)
    print(f"{'序号':<6} {'人员':<10} {'地点':<10} {'日期':<15} {'雷管数':<10} {'炸药数':<10}")
    print("-" * 90)
    
    total_leiguan = 0
    total_zayao = 0
    
    for data in data_list:
        print(f"{data.get('序号', ''):<6} {data['人员']:<10} {data['地点']:<10} {data['日期']:<15} {data['雷管数']:<10} {data['炸药数']:<10}")
        total_leiguan += data['雷管数']
        total_zayao += data['炸药数']
    
    print("-" * 90)
    print(f"{'合计':<6} {'':<10} {'':<10} {'':<15} {total_leiguan:<10} {total_zayao:<10}")
    print("=" * 90)
    
    return {
        "total_records": len(data_list),
        "total_leiguan": total_leiguan,
        "total_zayao": total_zayao
    }


def generate_sql_insert(data_list, table_name="blasting_records"):
    """生成SQL插入语句"""
    sql_list = []
    
    for data in data_list:
        sql = f"""INSERT INTO {table_name} (人员, 地点, 日期, 雷管数, 炸药数)
VALUES ('{data['人员']}', '{data['地点']}', '{data['日期']}', {data['雷管数']}, {data['炸药数']});"""
        sql_list.append(sql)
    
    return sql_list


def export_to_json(data_list, filename="blasting_summary.json"):
    """导出为JSON文件"""
    import json
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)
    
    print(f"已导出到 {filename}")


def export_to_csv(data_list, filename="blasting_summary.csv"):
    """导出为CSV文件"""
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        if data_list:
            writer = csv.DictWriter(f, fieldnames=['序号', '人员', '地点', '日期', '雷管数', '炸药数'])
            writer.writeheader()
            writer.writerows(data_list)
    
    print(f"已导出到 {filename}")

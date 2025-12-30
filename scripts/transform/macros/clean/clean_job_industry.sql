{% macro clean_job_industry(column_name) %}

{% set clean_col = remove_accents(column_name) %}
    CASE
        -- IT & Software
        WHEN {{ clean_col }} ~ '(it|cong nghe thong tin|cntt|phan mem|software|it services|it consulting|software products|web services|software development|it hardware|computing|software development outsourcing|phan cung|mang)' THEN 'Công nghệ thông tin & Phần mềm'
        
        -- Finance & Banking
        WHEN {{ clean_col }} ~ '(ngan hang|tai chinh|financial services|banking|insurance|bao hiem|chung khoan|dau tu|investment|fintech|chung khoan / vang / ngoai te)' THEN 'Tài chính & Ngân hàng'
        
        -- E-commerce & Retail
        WHEN {{ clean_col }} ~ '(thuong mai dien tu|e-commerce|ban le|ban si|retail|ecommerce|shopping)' THEN 'Thương mại điện tử & Bán lẻ'
        
        -- Manufacturing & Industrial
        WHEN {{ clean_col }} ~ '(san xuat|manufacturing|production|factory|industrial|cong nghiep|co khi|may moc|thiet bi cong nghiep|tu dong hoa|det may|may mac|giay dep|da giay)' THEN 'Sản xuất & Công nghiệp'
        
        -- Real Estate & Construction
        WHEN {{ clean_col }} ~ '(bat dong san|cho thue|real estate|property|housing|construction|xay dung)' THEN 'Bất động sản & Xây dựng'
        
        -- Transportation & Logistics
        WHEN {{ clean_col }} ~ '(van tai|transportation|logistics|hau can|giao nhan|warehouse|kho van|shipping|supply chain|chuoi cung ung|nhap khau|xuat khau)' THEN 'Vận tải & Logistics'
        
        -- Energy & Utilities
        WHEN {{ clean_col }} ~ '(dien|dien tu|nang luong|energy|oil|gas|dau khi|khai khoang|renewable|solar|wind|power|san xuat va phan phoi dien|khi dot|nuoc)' THEN 'Năng lượng & Tiện ích'
        
        -- Healthcare & Medical
        WHEN {{ clean_col }} ~ '(y te|suc khoe|healthcare|medical|pharmaceutical|hospital|health|medicine|thiet bi y te|duoc pham)' THEN 'Y tế & Chăm sóc sức khỏe'
        
        -- Consumer Goods
        WHEN {{ clean_col }} ~ '(food|hang tieu dung|consumer goods|ban le|ban si|thuc pham|do uong|hang gia dung|my pham|trang suc|thoi trang|bao bi|in an|dan nhan)' THEN 'Hàng tiêu dùng'
        
        -- Chemical & Bio
        WHEN {{ clean_col }} ~ '(hoa chat|hoa sinh|chemical|bio|pharmaceutical)' THEN 'Hóa chất & Sinh học'
        
        -- Education & Training
        WHEN {{ clean_col }} ~ '(giao duc|dao tao|education|training|academic|university|college)' THEN 'Giáo dục & Đào tạo'
        
        -- Hospitality & Tourism
        WHEN {{ clean_col }} ~ '(dich vu luu tru|nha hang|khach san|du lich|hospitality|tourism|restaurant|hotel)' THEN 'Khách sạn & Du lịch'
        
        -- Automotive
        WHEN {{ clean_col }} ~ '(o to|automotive|car|vehicle)' THEN 'Ô tô & Xe cộ'
        
        -- Telecommunications
        WHEN {{ clean_col }} ~ '(vien thong|telecommunications|telecom|networking|mobile|wireless)' THEN 'Viễn thông'
        
        -- Accounting & Auditing
        WHEN {{ clean_col }} ~ '(ke toan|kiem toan|accounting|auditing|bookkeeping)' THEN 'Kế toán & Kiểm toán'
        
        -- Marketing & Communications
        WHEN {{ clean_col }} ~ '(marketing|truyen thong|quang cao|khuyen mai|doi ngoai|marketing / truyen thong / quang cao|digital marketing|branding|advertising|pr|promotion|phat trien thi truong)' THEN 'Marketing & Truyền thông'
        
        -- Government & NGO
        WHEN {{ clean_col }} ~ '(chinh phu|ngo|government|public sector|administrative|state|federal)' THEN 'Chính phủ & Tổ chức phi lợi nhuận'
        
        -- Agriculture & Forestry
        WHEN {{ clean_col }} ~ '(nong nghiep|lam nghiep|nuoi trong thuy san|agriculture|forestry|farming|agritech|crop|livestock)' THEN 'Nông nghiệp & Lâm nghiệp'
        
        -- Human Resources
        WHEN {{ clean_col }} ~ '(nhan su|human resources|hr|recruitment|tuyen dung|personnel)' THEN 'Nhân sự'
        
        -- Administration & Office
        WHEN {{ clean_col }} ~ '(hanh chinh|van phong|thu ky|tro ly|administration|office|clerical)' THEN 'Hành chính & Văn phòng'
        
        -- Consulting & Customer Service
        WHEN {{ clean_col }} ~ '(tu van|cham soc khach hang|consulting|customer service|support|service|help desk|advisory|consultant)' THEN 'Tư vấn & Chăm sóc khách hàng'
        
        -- Arts & Design
        WHEN {{ clean_col }} ~ '(game|nghe thuat|thiet ke|giai tri|arts|design|entertainment|media)' THEN 'Nghệ thuật & Thiết kế'
        
        -- Data & Analytics (Specialized)
        WHEN {{ clean_col }} ~ '(kinh doanh|data science|khoa hoc du lieu|data analytics|phan tich du lieu|business analytics|phan tich kinh doanh|business intelligence|tri tue kinh doanh|bi|analytics|analysis|data engineering|ky thuat du lieu|machine learning|hoc may|artificial intelligence|tri tue nhan tao|ai|big data|data mining|data visualization|truc quan hoa du lieu)' THEN 'Dữ liệu & Phân tích'
        
        -- Other specific industries
        WHEN {{ clean_col }} ~ '(spa|lam dep|beauty|spa)' THEN 'Làm đẹp & Chăm sóc sức khỏe'
        WHEN {{ clean_col }} ~ '(nguoi giup viec|phuc vu|tap vu|domestic helper|cleaning|janitorial)' THEN 'Dịch vụ gia đình'
        ELSE 'Khác'
    END as job_industry,

    CASE
        WHEN {{clean_col}} ~ '(,)' THEN TRUE
        ELSE FALSE
    END as has_other_industry 

{% endmacro %}
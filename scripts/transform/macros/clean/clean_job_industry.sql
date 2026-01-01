{% macro clean_job_industry(column_name) %}

{% set clean_col = remove_accents(column_name) %}
    CASE
        -- IT & Software
        WHEN {{ clean_col }} ~ '(it|cong nghe thong tin|cntt|phan mem|software|it services|it consulting|software products|web services|software development|it hardware|computing|phan cung|mang)' THEN 'Công nghệ thông tin & Phần mềm'
        
        -- Data & Analytics
        WHEN {{ clean_col }} ~ '(data science|khoa hoc du lieu|data analytics|phan tich du lieu|business analytics|business intelligence|tri tue kinh doanh|bi|analytics|analysis|data engineering|ky thuat du lieu|machine learning|hoc may|artificial intelligence|tri tue nhan tao|ai|big data|data mining|data visualization|truc quan hoa du lieu|data architect|data quality|data warehouse|etl|dbms|database|sql|thong ke|statistics)' THEN 'Dữ liệu & Phân tích'

        -- Cybersecurity & Network Security
        WHEN {{ clean_col }} ~ '(cybersecurity|an ninh mang|bao mat|information security|network security|computer security|penetration testing|vulnerability|firewall|intrusion detection|threat intelligence|security operations|incident response|ciso|identity management|access control|authentication|encryption|cryptography|zero trust)' THEN 'An ninh mạng & Bảo mật'
        
        -- Finance, Banking & Insurance
        WHEN {{ clean_col }} ~ '(ngan hang|tai chinh|financial services|banking|insurance|bao hiem|chung khoan|securities|dau tu|investment|fintech|risk management|actuarial|underwriting|claims|policy|coverage|liability)' THEN 'Tài chính / Ngân hàng / Bảo hiểm'
        
        -- Sales & Business Development
        WHEN {{ clean_col }} ~ '(kinh doanh|ban hang|sales|business development|account executive|account manager|phat trien thi truong|telesales|kinh doanh quoc te|dai ly|phan phoi|sales engineer|ky su kinh doanh|merchandiser)' THEN 'Kinh doanh / Bán hàng'

        -- Marketing & Communications
        WHEN {{ clean_col }} ~ '(marketing|truyen thong|quang cao|digital marketing|branding|advertising|pr|promotion|content|copywriter|social media|event|to chuc su kien|bao chi|media|public relations)' THEN 'Marketing & Truyền thông'

        -- E-commerce & Retail
        WHEN {{ clean_col }} ~ '(thuong mai dien tu|e-commerce|ban le|ban si|retail|ecommerce|shopping|online marketplace|digital marketplace|shopee|lazada|tiki|tiktok shop|wholesale)' THEN 'Thương mại điện tử & Bán lẻ'
        
        -- Manufacturing & Industrial
        WHEN {{ clean_col }} ~ '(san xuat|manufacturing|production|factory|industrial|cong nghiep|tu dong hoa|det may|may mac|giay dep|da giay|in an|packaging|bao bi)' THEN 'Sản xuất & Công nghiệp'

        -- Engineering, Mechanics & Electronics
        WHEN {{ clean_col }} ~ '(co khi|may moc|thiet bi cong nghiep|ky thuat|engineering|mechanical|electrical|electronics|dien tu|dien lanh|mechatronics|co dien|m&e|vba|cad|cam|cae)' THEN 'Kỹ thuật / Cơ khí / Điện & Điện tử'
        
        -- Real Estate & Construction
        WHEN {{ clean_col }} ~ '(bat dong san|real estate|property|housing|construction|xay dung|kien truc|architect|noi that|interior design|cho thue|dia oc)' THEN 'Bất động sản & Xây dựng'
        
        -- Transportation & Logistics
        WHEN {{ clean_col }} ~ '(van tai|transportation|logistics|hau can|giao nhan|warehouse|kho van|shipping|supply chain|chuoi cung ung|nhap khau|xuat khau|import|export|customs|thong quan|freight|maritime|hang hai)' THEN 'Vận tải & Logistics'
        
        -- Healthcare & Pharmaceutical
        WHEN {{ clean_col }} ~ '(y te|suc khoe|healthcare|medical|pharmaceutical|hospital|health|medicine|thiet bi y te|duoc pham|bio|biotechnology|biopharma|clinical research|life sciences|molecular biology|genetics|y duoc|bac si|dieu duong)' THEN 'Y tế / Dược phẩm / Chăm sóc sức khỏe'

        -- Energy, Utilities & Environment
        WHEN {{ clean_col }} ~ '(dien|nang luong|energy|oil|gas|dau khi|khai khoang|renewable|solar|wind|power|san xuat va phan phoi dien|khi dot|nuoc|utilities|environmental|moi truong|waste management|recycling|sustainability|geology|dia chat)' THEN 'Năng lượng / Môi trường / Tiện ích'
        
        -- Consumer Goods (FMCG)
        WHEN {{ clean_col }} ~ '(food|hang tieu dung|fmcg|consumer goods|ban le|ban si|thuc pham|do uong|hang gia dung|my pham|trang suc|thoi trang|dan nhan)' THEN 'Hàng tiêu dùng'
        
        -- Education & Training
        WHEN {{ clean_col }} ~ '(giao duc|dao tao|education|training|academic|university|college|giang day|teaching|tu van du hoc|library|thu vien)' THEN 'Giáo dục & Đào tạo'
        
        -- Hospitality & Tourism
        WHEN {{ clean_col }} ~ '(dich vu luu tru|nha hang|khach san|du lich|hospitality|tourism|restaurant|hotel|f&b|am thuc|an uong|tourist|travel|be_p|chef)' THEN 'Khách sạn & Du lịch'
        
        -- Automotive
        WHEN {{ clean_col }} ~ '(o to|automotive|car|vehicle|xe may|phu tung)' THEN 'Ô tô & Xe cộ'
        
        -- Telecommunications
        WHEN {{ clean_col }} ~ '(vien thong|telecommunications|telecom|networking|mobile|wireless|isp)' THEN 'Viễn thông'
        
        -- Accounting & Auditing
        WHEN {{ clean_col }} ~ '(ke toan|kiem toan|accounting|auditing|bookkeeping|thue|tax)' THEN 'Kế toán & Kiểm toán'
        
        -- Human Resources
        WHEN {{ clean_col }} ~ '(nhan su|human resources|hr|recruitment|tuyen dung|headhunt|luong thuong|payroll|benefit)' THEN 'Nhân sự'
        
        -- Administration & Office
        WHEN {{ clean_col }} ~ '(hanh chinh|van phong|thu ky|tro ly|administration|office|clerical|le tan|receptionist|pa|ea|tro ly|bi thu)' THEN 'Hành chính & Văn phòng'

        -- Management & Executive
        WHEN {{ clean_col }} ~ '(quan ly dieu hanh|ceo|director|executive|manager|leader|truong phong|pho phong|quan ly|management|trinh duoc vien)' THEN 'Quản lý / Điều hành'
        
        -- Consulting & Customer Service
        WHEN {{ clean_col }} ~ '(tu van|cham soc khach hang|consulting|customer service|support|service|help desk|advisory|consultant|call center|telesales)' THEN 'Tư vấn & Chăm sóc khách hàng'
        
        -- Arts, Design & Entertainment
        WHEN {{ clean_col }} ~ '(game|nghe thuat|thiet ke|giai tri|arts|design|entertainment|media|graphic|creative|sang tao|am nhac|music|phim|movie|video|photography|nhiep anh)' THEN 'Nghệ thuật & Thiết kế'
        
        -- Legal Services
        WHEN {{ clean_col }} ~ '(legal|law|luat|lawyer|attorney|phap ly|phap che|court|judicial|solicitor|phap luat)' THEN 'Dịch vụ pháp lý'

        -- Languages, Translation & Interpretation
        WHEN {{ clean_col }} ~ '(ngon ngu|bien phien dich|translator|interpreter|translation|interpretation|tieng anh|tieng nhat|tieng trung|tieng han|english|japanese|chinese|korean|linguistics)' THEN 'Ngôn ngữ / Biên phiên dịch'

        -- Agriculture, Forestry & Fishery
        WHEN {{ clean_col }} ~ '(nong nghiep|lam nghiep|thuy san|agriculture|forestry|farming|agritech|nuoi trong|hai san|fishery|animal husbandry|veterinary|thu y|thuy loi|irrigation)' THEN 'Nông nghiệp / Lâm nghiệp / Thủy sản'

        -- Aerospace & Defense
        WHEN {{ clean_col }} ~ '(aerospace|aviation|defense|aircraft|hang khong|bay|quan su|military|pilot|phi cong)' THEN 'Hàng không & Quốc phòng'

        -- Beauty & Personal Care
        WHEN {{ clean_col }} ~ '(spa|lam dep|beauty|tham my|salon|fitness|gym|the hinh|personal care)' THEN 'Làm đẹp & Chăm sóc sức khỏe'

        -- Unskilled Workers & Security
        WHEN {{ clean_col }} ~ '(lao dong pho thong|unskilled|manual labor|cong nhan|worker|security|bao ve|ve si|giup viec|domestic helper|cleaning|tap vu)' THEN 'Lao động phổ thông / Bảo vệ'

        -- Government & NGO
        WHEN {{ clean_col }} ~ '(chinh phu|ngo|government|public sector|administrative|phi chinh phu|to chuc quoc te|non-profit)' THEN 'Chính phủ & Tổ chức phi lợi nhuận'

        ELSE 'Khác'
    END as job_industry,

    CASE
        WHEN {{clean_col}} ~ '(,)' THEN TRUE
        ELSE FALSE
    END as has_other_industry 

{% endmacro %}

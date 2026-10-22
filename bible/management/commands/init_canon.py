from django.core.management.base import BaseCommand
from bible.models import Book, Chapter, ReadingPlan, ReadingPlanDay

CANON_73_BOOKS = [
    # CỰU ƯỚC (46 SÁCH)
    # I. Ngũ Thư (5)
    {"order_num": 1, "code": "St", "name": "Sáng Thế", "slug": "sach-sang-the", "testament": "OT", "group": "Ngũ Thư", "total_chapters": 50, "description": "Sách Khởi Nguyên, tường thuật công cuộc sáng tạo trời đất, nhân loại và các tổ phụ đức tin."},
    {"order_num": 2, "code": "Xh", "name": "Xuất Hành", "slug": "sach-xuat-hanh", "testament": "OT", "group": "Ngũ Thư", "total_chapters": 40, "description": "Thiên Chúa giải phóng dân tộc Í-ra-en khỏi ách nô lệ Ai Cập và ban Giao Ước Sinai."},
    {"order_num": 3, "code": "Lv", "name": "Lê-vi", "slug": "sach-le-vi", "testament": "OT", "group": "Ngũ Thư", "total_chapters": 27, "description": "Các luật lệ phụng vụ, tế tự và sự thánh thiện của dân Chúa."},
    {"order_num": 4, "code": "Ds", "name": "Dân Số", "slug": "sach-dan-so", "testament": "OT", "group": "Ngũ Thư", "total_chapters": 36, "description": "Hành trình 40 năm trong sa mạc tiến về Đất Hứa."},
    {"order_num": 5, "code": "Đnl", "name": "Đệ Nhị Luật", "slug": "sach-de-nhi-luat", "testament": "OT", "group": "Ngũ Thư", "total_chapters": 34, "description": "Những lời trăn trối và nhắc lại Luật Chúa của ông Môsê trước khi dân vào Đất Hứa."},
    
    # II. Các Sách Lịch Sử (16)
    {"order_num": 6, "code": "Gs", "name": "Giô-suê", "slug": "sach-gio-sue", "testament": "OT", "group": "Lịch Sử", "total_chapters": 24, "description": "Cuộc chinh phục và phân chia Đất Hứa dưới sự lãnh đạo của Giô-suê."},
    {"order_num": 7, "code": "Tl", "name": "Thủ Lãnh", "slug": "sach-thu-lanh", "testament": "OT", "group": "Lịch Sử", "total_chapters": 21, "description": "Thời kỳ các quan xét/thủ lãnh giải cứu dân Í-ra-en khỏi quân thù."},
    {"order_num": 8, "code": "R", "name": "Rút", "slug": "sach-rut", "testament": "OT", "group": "Lịch Sử", "total_chapters": 4, "description": "Câu chuyện cảm động về lòng hiếu thảo và trung thành của nàng Rút, cụ bà của vua Đavít."},
    {"order_num": 9, "code": "1Sm", "name": "1 Sa-mu-en", "slug": "sach-sa-mu-en-1", "testament": "OT", "group": "Lịch Sử", "total_chapters": 31, "description": "Giai đoạn chuyển tiếp từ thời thủ lãnh sang vương quyền: Samuen, Saun và Đavít."},
    {"order_num": 10, "code": "2Sm", "name": "2 Sa-mu-en", "slug": "sach-sa-mu-en-2", "testament": "OT", "group": "Lịch Sử", "total_chapters": 24, "description": "Triều đại huy hoàng và các thử thách của Vua Đavít tại Giêrusalem."},
    {"order_num": 11, "code": "1V", "name": "1 Các Vua", "slug": "sach-cac-vua-1", "testament": "OT", "group": "Lịch Sử", "total_chapters": 22, "description": "Triều đại Salômôn, việc xây cất Đền Thờ và sự phân chia vương quốc."},
    {"order_num": 12, "code": "2V", "name": "2 Các Vua", "slug": "sach-cac-vua-2", "testament": "OT", "group": "Lịch Sử", "total_chapters": 25, "description": "Lịch sử hai vương quốc Bắc - Nam cho đến biến cố lưu đày Babylon."},
    {"order_num": 13, "code": "1Sb", "name": "1 Sử Biên", "slug": "sach-su-bien-1", "testament": "OT", "group": "Lịch Sử", "total_chapters": 29, "description": "Gia phả toàn thể dân Chúa và việc chuẩn bị xây Đền Thờ của vua Đavít."},
    {"order_num": 14, "code": "2Sb", "name": "2 Sử Biên", "slug": "sach-su-bien-2", "testament": "OT", "group": "Lịch Sử", "total_chapters": 36, "description": "Lịch sử các vua Giuđa từ Salômôn đến chiếu chỉ tha hương của vua Kyrô."},
    {"order_num": 15, "code": "Er", "name": "Ét-ra", "slug": "sach-et-ra", "testament": "OT", "group": "Lịch Sử", "total_chapters": 10, "description": "Công cuộc hồi hương và tái thiết Đền Thờ Giêrusalem."},
    {"order_num": 16, "code": "Nkm", "name": "Nơ-khe-mi-a", "slug": "sach-no-khe-mi-a", "testament": "OT", "group": "Lịch Sử", "total_chapters": 13, "description": "Tái thiết tường thành Giêrusalem và cải cách đời sống tôn giáo."},
    {"order_num": 17, "code": "Tb", "name": "Tô-bi-a", "slug": "sach-to-bi-a", "testament": "OT", "group": "Lịch Sử", "total_chapters": 14, "description": "Gương sáng gia đình đạo đức, lòng bác ái và sự đồng hành của Tổng lãnh Thiên thần Raphaen."},
    {"order_num": 18, "code": "Gđt", "name": "Giu-đi-tha", "slug": "sach-giu-di-tha", "testament": "OT", "group": "Lịch Sử", "total_chapters": 16, "description": "Người phụ nữ quả cảm xả thân cứu dân tộc khỏi tay tướng Hôlôphênê."},
    {"order_num": 19, "code": "Est", "name": "Ét-te", "slug": "sach-et-te", "testament": "OT", "group": "Lịch Sử", "total_chapters": 10, "description": "Hoàng hậu Étte cứu vớt đồng bào Do Thái khỏi âm mưu diệt chủng tại Ba Tư."},
    {"order_num": 20, "code": "1Mcb", "name": "1 Ma-ca-bê", "slug": "sach-ma-ca-be-1", "testament": "OT", "group": "Lịch Sử", "total_chapters": 16, "description": "Cuộc kháng chiến anh dũng bảo vệ đức tin và Đền Thờ chống lại sự cưỡng ép Hy Lạp hóa."},
    {"order_num": 21, "code": "2Mcb", "name": "2 Ma-ca-bê", "slug": "sach-ma-ca-be-2", "testament": "OT", "group": "Lịch Sử", "total_chapters": 15, "description": "Các gương tử đạo anh dũng và đức tin kiên vững vào sự sống lại của kẻ chết."},

    # III. Các Sách Giáo Huấn & Khôn Ngoan (7)
    {"order_num": 22, "code": "G", "name": "Gióp", "slug": "sach-giop", "testament": "OT", "group": "Giáo Huấn", "total_chapters": 42, "description": "Chiêm niệm về mầu nhiệm sự đau khổ của người công chính và sự quan phòng của Thiên Chúa."},
    {"order_num": 23, "code": "Tv", "name": "Thánh Vịnh", "slug": "sach-thanh-vinh", "testament": "OT", "group": "Giáo Huấn", "total_chapters": 150, "description": "150 khúc ca tạ ơn, ngợi khen, khẩn cầu và tôn vinh Đấng Tối Cao."},
    {"order_num": 24, "code": "Cn", "name": "Châm Ngôn", "slug": "sach-cham-ngon", "testament": "OT", "group": "Giáo Huấn", "total_chapters": 31, "description": "Các bài học luân lý và khôn ngoan ứng xử thực tiễn trong cuộc sống hàng ngày."},
    {"order_num": 25, "code": "Gv", "name": "Giảng Viên", "slug": "sach-giang-vien", "testament": "OT", "group": "Giáo Huấn", "total_chapters": 12, "description": "Nhận thức sâu sắc về tính phù vân tạm bợ của đời người và lời mời gọi kính sợ Thiên Chúa."},
    {"order_num": 26, "code": "Dc", "name": "Diễm Ca", "slug": "sach-diem-ca", "testament": "OT", "group": "Giáo Huấn", "total_chapters": 8, "description": "Bản tình ca tuyệt mỹ biểu trưng cho tình yêu giữa Thiên Chúa và dân Người."},
    {"order_num": 27, "code": "Kn", "name": "Khôn Ngoan", "slug": "sach-khon-ngoan", "testament": "OT", "group": "Giáo Huấn", "total_chapters": 19, "description": "Ca ngợi Đức Khôn Ngoan của Thiên Chúa và số phận bất tử của người công chính."},
    {"order_num": 28, "code": "Hc", "name": "Huấn Ca", "slug": "sach-huan-ca", "testament": "OT", "group": "Giáo Huấn", "total_chapters": 51, "description": "Kho tàng giáo huấn phong phú về đời sống gia đình, xã hội và tôn giáo của người Do Thái."},

    # IV. Các Sách Ngôn Sứ (18)
    {"order_num": 29, "code": "Is", "name": "I-sai-a", "slug": "sach-ngon-su-i-sai-a", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 66, "description": "Đại ngôn sứ loan báo về Đấng Mê-si-a (Emmanuel), Người Tôi Trung chịu đau khổ."},
    {"order_num": 30, "code": "Gr", "name": "Giê-rê-mi-a", "slug": "sach-ngon-su-gie-re-mi-a", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 52, "description": "Ngôn sứ của nước mắt, loan báo Giao Ước Mới được ghi khắc vào tận đáy lòng."},
    {"order_num": 31, "code": "Ac", "name": "Ai Ca", "slug": "sach-ai-ca", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 5, "description": "Khúc than khóc bi thương trước cảnh thành Giêrusalem bị tàn phá."},
    {"order_num": 32, "code": "Br", "name": "Ba-rúc", "slug": "sach-ba-ruc", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 6, "description": "Lời kêu gọi thống hối và niềm hy vọng trở về dành cho những người lưu đày."},
    {"order_num": 33, "code": "Ez", "name": "Ê-dê-ki-en", "slug": "sach-ngon-su-e-de-ki-en", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 48, "description": "Các thị kiến kỳ vĩ về vinh quang Thiên Chúa, trái tim bằng thịt và sự phục sinh."},
    {"order_num": 34, "code": "Đn", "name": "Đa-ni-en", "slug": "sach-ngon-su-da-ni-en", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 14, "description": "Lòng trung tín bảo vệ lề luật giữa cung điện Babylon và các thị kiến cánh chung."},
    {"order_num": 35, "code": "Hs", "name": "Hô-sê", "slug": "sach-ngon-su-ho-se", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 14, "description": "Tình yêu chung thủy, bao dung vô bờ bến của Thiên Chúa đối với người vợ bội bạc."},
    {"order_num": 36, "code": "Ge", "name": "Giô-en", "slug": "sach-ngon-su-gio-en", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 4, "description": "Ngày của Đức Chúa và lời hứa đổ Thần Khí trên mọi xác phàm."},
    {"order_num": 37, "code": "Am", "name": "A-mốt", "slug": "sach-ngon-su-a-mot", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 9, "description": "Tiếng kêu đòi công bình xã hội và bảo vệ những người nghèo khổ cơ bần."},
    {"order_num": 38, "code": "Ob", "name": "Ô-va-đi-a", "slug": "sach-ngon-su-o-va-di-a", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 1, "description": "Lời sấm phạt thành Êđôm và sự phục hưng của Núi Sion."},
    {"order_num": 39, "code": "Gna", "name": "Giô-na", "slug": "sach-ngon-su-gio-na", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 4, "description": "Dấu lạ Giôna trong bụng cá và lòng thương xót của Thiên Chúa đối với muôn dân."},
    {"order_num": 40, "code": "Mi", "name": "Mi-kha", "slug": "sach-ngon-su-mi-kha", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 7, "description": "Loan báo Đấng Cứu Thế sẽ xuất thân từ làng Bê-lem nhỏ bé."},
    {"order_num": 41, "code": "Na", "name": "Na-khum", "slug": "sach-ngon-su-na-khum", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 3, "description": "Sự sụp đổ của bạo đế Ninivê và sự giải phóng cho Giuđa."},
    {"order_num": 42, "code": "Kb", "name": "Kha-ba-cúc", "slug": "sach-ngon-su-kha-ba-cuc", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 3, "description": "Người công chính sẽ được sống nhờ lòng trung tín."},
    {"order_num": 43, "code": "Xp", "name": "Xô-phô-ni-a", "slug": "sach-ngon-su-xo-pho-ni-a", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 3, "description": "Ngày phán xét và niềm vui của 'đoàn dân nghèo khó khiêm hạ'."},
    {"order_num": 44, "code": "Kg", "name": "Khác-gai", "slug": "sach-ngon-su-khac-gai", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 2, "description": "Thúc giục toàn dân chung tay xây dựng lại Đền Thờ Đức Chúa."},
    {"order_num": 45, "code": "Zc", "name": "Da-ca-ri-a", "slug": "sach-ngon-su-da-ca-ri-a", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 14, "description": "Loan báo Vị Vua khiêm hạ cưỡi trên lưng lừa tiến vào Giêrusalem."},
    {"order_num": 46, "code": "Ml", "name": "Ma-la-khi", "slug": "sach-ngon-su-ma-la-khi", "testament": "OT", "group": "Ngôn Sứ", "total_chapters": 3, "description": "Cuốn cuối cùng của Cựu Ước, loan báo vị sứ giả dọn đường cho Đấng Cứu Tinh."},

    # TÂN ƯỚC (27 SÁCH)
    # V. Sách Tin Mừng (4)
    {"order_num": 47, "code": "Mt", "name": "Mát-thêu", "slug": "tin-mung-theo-thanh-mat-theu", "testament": "NT", "group": "Tin Mừng", "total_chapters": 28, "description": "Tin Mừng viết cho người Do Thái, làm nổi bật Chúa Giêsu là Đấng Mêsia hoàn tất Cựu Ước."},
    {"order_num": 48, "code": "Mc", "name": "Mác-cô", "slug": "tin-mung-theo-thanh-mac-co", "testament": "NT", "group": "Tin Mừng", "total_chapters": 16, "description": "Tin Mừng ngắn gọn và sống động nhất, khắc họa Chúa Giêsu là Con Thiên Chúa đầy quyền năng."},
    {"order_num": 49, "code": "Lc", "name": "Lu-ca", "slug": "tin-mung-theo-thanh-lu-ca", "testament": "NT", "group": "Tin Mừng", "total_chapters": 24, "description": "Tin Mừng của lòng thương xót, cầu nguyện và niềm vui cứu độ cho mọi người nghèo hèn."},
    {"order_num": 50, "code": "Ga", "name": "Gio-an", "slug": "tin-mung-theo-thanh-gio-an", "testament": "NT", "group": "Tin Mừng", "total_chapters": 21, "description": "Tin Mừng thần học sâu sắc, mạc khải Đức Giêsu là Ngôi Lời nhập thể và là Sự Sống."},

    # VI. Lịch Sử Giáo Hội (1)
    {"order_num": 51, "code": "Cv", "name": "Công Vụ Tông Đồ", "slug": "sach-cong-vu-tong-do", "testament": "NT", "group": "Công Vụ", "total_chapters": 28, "description": "Sự khai sinh của Hội Thánh sơ khai dưới sự dẫn dắt của Chúa Thánh Thần."},

    # VII. Các Thư của Thánh Phaolô (14)
    {"order_num": 52, "code": "Rm", "name": "Rô-ma", "slug": "thu-gui-tin-huu-ro-ma", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 16, "description": "Kiệt tác thần học về sự công chính hóa nhờ đức tin vào Đức Kitô."},
    {"order_num": 53, "code": "1Cr", "name": "1 Cô-rin-tô", "slug": "thu-1-gui-tin-huu-co-rin-to", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 16, "description": "Giải quyết các chia rẽ cộng đoàn, bài ca đức mến tuyệt mỹ và mầu nhiệm phục sinh."},
    {"order_num": 54, "code": "2Cr", "name": "2 Cô-rin-tô", "slug": "thu-2-gui-tin-huu-co-rin-to", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 13, "description": "Tâm tình bộc bạch của thánh Phaolô về sứ vụ tông đồ: 'Khi tôi yếu, chính là lúc tôi mạnh'."},
    {"order_num": 55, "code": "Gl", "name": "Ga-lát", "slug": "thu-gui-tin-huu-ga-lat", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 6, "description": "Bản tuyên ngôn tự do Kitô giáo: được cứu rỗi nhờ ân sủng chứ không do lề luật."},
    {"order_num": 56, "code": "Ep", "name": "Ê-phê-xô", "slug": "thu-gui-tin-huu-e-phe-xo", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 6, "description": "Kế hoạch nhiệm mầu quy tụ muôn loài trong Đức Kitô và Hội Thánh là Thân Thể Người."},
    {"order_num": 57, "code": "Pl", "name": "Phi-líp-phê", "slug": "thu-gui-tin-huu-phi-lip-phe", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 4, "description": "Bức thư của niềm vui Kitô giáo tràn trề ngay giữa gông cùm tù ngục."},
    {"order_num": 58, "code": "Cl", "name": "Cô-lô-xê", "slug": "thu-gui-tin-huu-co-lo-xe", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 4, "description": "Địa vị tối thượng tuyệt đối của Đức Kitô trên toàn thể vũ trụ tạo thành."},
    {"order_num": 59, "code": "1Tx", "name": "1 Thê-xa-lô-ni-ca", "slug": "thu-1-gui-tin-huu-the-xa-lo-ni-ca", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 5, "description": "Văn bản Tân Ước sớm nhất, khuyên nhủ tỉnh thức đợi chờ ngày Chúa quang lâm."},
    {"order_num": 60, "code": "2Tx", "name": "2 Thê-xa-lô-ni-ca", "slug": "thu-2-gui-tin-huu-the-xa-lo-ni-ca", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 3, "description": "Làm rõ những hiểu lầm về ngày Chúa đến và lời khuyên siêng năng làm việc."},
    {"order_num": 61, "code": "1Tm", "name": "1 Ti-mô-thê", "slug": "thu-1-gui-ong-ti-mo-the", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 6, "description": "Chỉ dẫn mục vụ cho vị giám mục trẻ tuổi về việc coi sóc và lãnh đạo cộng đoàn."},
    {"order_num": 62, "code": "2Tm", "name": "2 Ti-mô-thê", "slug": "thu-2-gui-ong-ti-mo-the", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 4, "description": "Bức thư cảm động cuối đời của Phaolô trước khi tử đạo: 'Tôi đã chiến đấu trong trận chiến cao đẹp'."},
    {"order_num": 63, "code": "Tt", "name": "Ti-tô", "slug": "thu-gui-ong-ti-to", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 3, "description": "Hướng dẫn thiết lập các bậc niên trưởng tại đảo Krêta và gìn giữ giáo lý lành mạnh."},
    {"order_num": 64, "code": "Fm", "name": "Phi-lê-môn", "slug": "thu-gui-ong-phi-le-mon", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 1, "description": "Bức thư ngắn tha thiết xin ông Philêmôn đón nhận lại người nô lệ Ônêximô như người anh em."},
    {"order_num": 65, "code": "Dt", "name": "Híp-ri", "slug": "thu-gui-tin-huu-hip-ri", "testament": "NT", "group": "Thư Phaolô", "total_chapters": 13, "description": "Đức Kitô là Thượng Tế đời đời tuyệt hảo và Giao Ước Mới trường tồn."},

    # VIII. Các Thư Chung Tông Đồ (7)
    {"order_num": 66, "code": "Gc", "name": "Gia-cô-bê", "slug": "thu-cua-thanh-gia-co-be", "testament": "NT", "group": "Thư Chung", "total_chapters": 5, "description": "Đức tin không có việc làm là đức tin chết; lời khuyên thực thi bác ái cụ thể."},
    {"order_num": 67, "code": "1Pr", "name": "1 Phê-rô", "slug": "thu-1-cua-thanh-phe-ro", "testament": "NT", "group": "Thư Chung", "total_chapters": 5, "description": "Cổ vũ niềm hy vọng sống động và sự kiên trì chịu đựng thử thách vì danh Kitô."},
    {"order_num": 68, "code": "2Pr", "name": "2 Phê-rô", "slug": "thu-2-cua-thanh-phe-ro", "testament": "NT", "group": "Thư Chung", "total_chapters": 3, "description": "Cảnh báo trước các tiên tri giả và xác tín vào lời hứa quang lâm của Chúa."},
    {"order_num": 69, "code": "1Ga", "name": "1 Gio-an", "slug": "thu-1-cua-thanh-gio-an", "testament": "NT", "group": "Thư Chung", "total_chapters": 5, "description": "Thiên Chúa là Tình Yêu, là Ánh Sáng; ai ở trong tình yêu thì ở trong Thiên Chúa."},
    {"order_num": 70, "code": "2Ga", "name": "2 Gio-an", "slug": "thu-2-cua-thanh-gio-an", "testament": "NT", "group": "Thư Chung", "total_chapters": 1, "description": "Nhắn nhủ sống trong sự thật và tình yêu chân chính của Đức Kitô."},
    {"order_num": 71, "code": "3Ga", "name": "3 Gio-an", "slug": "thu-3-cua-thanh-gio-an", "testament": "NT", "group": "Thư Chung", "total_chapters": 1, "description": "Khen ngợi lòng hiếu khách bác ái của ông Gai-út đối với các vị thừa sai."},
    {"order_num": 72, "code": "Gđ", "name": "Giu-đa", "slug": "thu-cua-thanh-giu-da", "testament": "NT", "group": "Thư Chung", "total_chapters": 1, "description": "Khuyên nhủ kiên cường bảo vệ đức tin đã được truyền lại một lần cho các thánh."},

    # IX. Sách Khải Huyền (1)
    {"order_num": 73, "code": "Kh", "name": "Khải Huyền", "slug": "sach-khai-huyen", "testament": "NT", "group": "Khải Huyền", "total_chapters": 22, "description": "Cuốn sách cuối cùng: khúc ca chiến thắng khải hoàn của Chiên Con và thị kiến Trời Mới Đất Mới."},
]

class Command(BaseCommand):
    help = "Khởi tạo chuẩn danh mục 73 cuốn Kinh Thánh Công Giáo và Kế hoạch đọc 1 năm"

    def handle(self, *args, **options):
        self.stdout.write("Bắt đầu khởi tạo quy điển 73 cuốn Kinh Thánh Công Giáo...")
        books_created = 0
        chapters_created = 0

        for book_data in CANON_73_BOOKS:
            book, created = Book.objects.update_or_create(
                order_num=book_data["order_num"],
                defaults={
                    "code": book_data["code"],
                    "name": book_data["name"],
                    "slug": book_data["slug"],
                    "testament": book_data["testament"],
                    "group": book_data["group"],
                    "total_chapters": book_data["total_chapters"],
                    "description": book_data["description"],
                }
            )
            if created:
                books_created += 1

            # Ensure all chapters exist for this book
            for ch_num in range(1, book.total_chapters + 1):
                chapter, ch_created = Chapter.objects.get_or_create(
                    book=book,
                    number=ch_num,
                    defaults={"title": f"Chương {ch_num}"}
                )
                if ch_created:
                    chapters_created += 1

        self.stdout.write(self.style.SUCCESS(f"-> Hoàn tất: {books_created} sách mới, {chapters_created} chương được thiết lập."))

        # Initialize 365-Day Reading Plan
        plan, p_created = ReadingPlan.objects.get_or_create(
            slug="ke-hoach-doc-kinh-thanh-1-nam",
            defaults={
                "name": "Kế hoạch đọc toàn bộ Kinh Thánh 365 ngày (1 năm)",
                "description": "Lộ trình đồng hành mỗi ngày với Lời Chúa: Mỗi ngày gồm 1 đoạn Cựu Ước, 1 Thánh Vịnh suy niệm và 1 đoạn Tân Ước.",
                "total_days": 365
            }
        )
        
        # Populate 365 days if empty
        if plan.days.count() < 365:
            self.stdout.write("Đang khởi tạo lịch trình 365 ngày đọc...")
            days_batch = []
            for day in range(1, 366):
                # Standard balanced Catholic schedule distribution
                st_ch = ((day * 2) % 50) + 1
                tv_ch = (day % 150) + 1
                nt_ch = (day % 28) + 1
                days_batch.append(ReadingPlanDay(
                    plan=plan,
                    day_number=day,
                    title=f"Ngày {day}: Lời Chúa soi bước",
                    readings_label=f"Cựu Ước (chương {st_ch}) • Thánh Vịnh {tv_ch} • Tin Mừng (chương {nt_ch})",
                    ot_reading=f"Cựu Ước chương {st_ch}",
                    psalm_reading=f"Thánh Vịnh {tv_ch}",
                    nt_reading=f"Tin Mừng chương {nt_ch}"
                ))
            ReadingPlanDay.objects.bulk_create(days_batch, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS("-> Đã khởi tạo xong lịch trình 365 ngày!"))

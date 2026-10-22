from django.core.management.base import BaseCommand
from bible.models import Book, Chapter, Verse

SAMPLE_DATA = [
    {
        "book_code": "St",
        "chapter_num": 1,
        "title": "Chương 1",
        "audio_url": "https://augustino.net/wp-content/uploads/audio/St-1.mp3",
        "verses": [
            {"num": 1, "section": "I. NGUỒN GỐC VŨ TRỤ VÀ NHÂN LOẠI", "sub": "Thiên Chúa sáng tạo trời đất", "text": "Lúc khởi đầu, Thiên Chúa sáng tạo trời đất."},
            {"num": 2, "sub": "", "text": "Đất còn trống rỗng, chưa có hình dạng, bóng tối bao trùm vực thẳm, và thần khí Thiên Chúa bay lượn trên mặt nước."},
            {"num": 3, "sub": "", "text": "Thiên Chúa phán: “Phải có ánh sáng.” Liền có ánh sáng."},
            {"num": 4, "sub": "", "text": "Thiên Chúa thấy rằng ánh sáng tốt đẹp. Thiên Chúa phân rẽ ánh sáng và bóng tối."},
            {"num": 5, "sub": "", "text": "Thiên Chúa gọi ánh sáng là “ngày”, bóng tối là “đêm”. Qua một buổi chiều và một buổi sáng: đó là ngày thứ nhất."},
            {"num": 6, "sub": "", "text": "Thiên Chúa phán: “Phải có một cái vòm ở giữa khối nước, để phân rẽ nước với nước.”"},
            {"num": 7, "sub": "", "text": "Thiên Chúa làm ra cái vòm đó và phân rẽ nước phía dưới vòm với nước phía trên. Liền có như vậy."},
            {"num": 8, "sub": "", "text": "Thiên Chúa gọi vòm đó là “trời”. Qua một buổi chiều và một buổi sáng: đó là ngày thứ hai."},
            {"num": 9, "sub": "", "text": "Thiên Chúa phán: “Nước phía dưới trời phải tụ lại một nơi, để chỗ cạn lộ ra.” Liền có như vậy."},
            {"num": 10, "sub": "", "text": "Thiên Chúa gọi chỗ cạn là “đất”, khối nước tụ lại là “biển”. Thiên Chúa thấy thế là tốt đẹp."},
            {"num": 11, "sub": "", "text": "Thiên Chúa phán: “Đất phải sinh thảo mộc xanh tươi, cỏ mang hạt giống, và cây trên mặt đất có trái, ra trái tùy theo loại, trong có hạt giống.” Liền có như vậy."},
            {"num": 12, "sub": "", "text": "Đất trổ sinh thảo mộc, cỏ mang hạt giống tùy theo loại, và cây ra trái, trong trái có hạt giống tùy theo loại. Thiên Chúa thấy thế là tốt đẹp."},
            {"num": 13, "sub": "", "text": "Qua một buổi chiều và một buổi sáng: đó là ngày thứ ba."},
            {"num": 14, "sub": "", "text": "Thiên Chúa phán: “Phải có những vầng sáng trên vòm trời, để phân rẽ ngày với đêm, để làm dấu chỉ xác định các đại lễ, ngày và năm."},
            {"num": 15, "sub": "", "text": "Đó sẽ là những vầng sáng trên vòm trời để chiếu soi mặt đất.” Liền có như vậy."},
            {"num": 16, "sub": "", "text": "Thiên Chúa làm ra hai vầng sáng lớn: vầng sáng lớn hơn để điều khiển ngày, vầng sáng nhỏ hơn để điều khiển đêm; Người cũng làm ra các ngôi sao."},
            {"num": 17, "sub": "", "text": "Thiên Chúa đặt các vầng sáng trên vòm trời để chiếu soi mặt đất,"},
            {"num": 18, "sub": "", "text": "để điều khiển ngày và đêm, và để phân rẽ ánh sáng với bóng tối. Thiên Chúa thấy thế là tốt đẹp."},
            {"num": 19, "sub": "", "text": "Qua một buổi chiều và một buổi sáng: đó là ngày thứ tư."},
            {"num": 20, "sub": "", "text": "Thiên Chúa phán: “Nước phải sinh ra đầy dẫy những sinh vật lúc nhúc, và loài chim phải bay lượn trên mặt đất, dưới vòm trời.”"},
            {"num": 21, "sub": "", "text": "Thiên Chúa sáng tạo các thủy quái khổng lồ, cùng mọi sinh vật vẫy vùng lúc nhúc dưới nước tùy theo loại, và mọi giống chim bay tùy theo loại. Thiên Chúa thấy thế là tốt đẹp."},
            {"num": 22, "sub": "", "text": "Thiên Chúa chúc phúc cho chúng rằng: “Hãy sinh sôi nảy nở thật nhiều, cho đầy biển; và chim phải sinh sản cho nhiều trên mặt đất.”"},
            {"num": 23, "sub": "", "text": "Qua một buổi chiều và một buổi sáng: đó là ngày thứ năm."},
            {"num": 24, "sub": "", "text": "Thiên Chúa phán: “Đất phải sinh ra các sinh vật tùy theo loại: gia súc, loài bò sát và dã thú tùy theo loại.” Liền có như vậy."},
            {"num": 25, "sub": "", "text": "Thiên Chúa làm ra dã thú tùy theo loại, gia súc tùy theo loại và loài bò sát dưới đất tùy theo loại. Thiên Chúa thấy thế là tốt đẹp."},
            {"num": 26, "sub": "Sáng tạo con người", "text": "Thiên Chúa phán: “Chúng ta hãy làm ra con người theo hình ảnh chúng ta, giống như chúng ta, để con người làm bá chủ cá biển, chim trời, gia súc, dã thú, tất cả mặt đất và mọi giống vật bò dưới đất.”"},
            {"num": 27, "sub": "", "text": "Thiên Chúa sáng tạo con người theo hình ảnh mình, Thiên Chúa sáng tạo con người theo hình ảnh Thiên Chúa, Thiên Chúa sáng tạo con người có nam có nữ."},
            {"num": 28, "sub": "", "text": "Thiên Chúa ban phúc lành cho họ, và Thiên Chúa phán với họ: “Hãy sinh sôi nảy nở thật nhiều, cho đầy mặt đất, và thống trị mặt đất. Hãy làm bá chủ cá biển, chim trời, và mọi giống vật bò trên mặt đất.”"},
            {"num": 29, "sub": "", "text": "Thiên Chúa phán: “Đây Ta ban cho các ngươi mọi thứ cỏ mang hạt giống trên khắp mặt đất, và mọi thứ cây có trái mang hạt giống, để làm lương thực cho các ngươi."},
            {"num": 30, "sub": "", "text": "Còn đối với mọi dã thú, chim trời và mọi vật bò dưới đất mà có sinh khí, thì Ta ban cho chúng mọi thứ cỏ xanh tươi để làm lương thực.” Liền có như vậy."},
            {"num": 31, "sub": "", "text": "Thiên Chúa thấy mọi sự Người đã làm ra quả là rất tốt đẹp! Qua một buổi chiều và một buổi sáng: đó là ngày thứ sáu."}
        ]
    },
    {
        "book_code": "Tv",
        "chapter_num": 23,
        "title": "Thánh Vịnh 23",
        "audio_url": "https://augustino.net/wp-content/uploads/audio/Tv-23.mp3",
        "verses": [
            {"num": 1, "section": "THÁNH VỊNH ĐAVÍT", "sub": "Chúa là mục tử chăn dắt tôi", "text": "Chúa là mục tử chăn dắt tôi, tôi chẳng thiếu thốn gì."},
            {"num": 2, "sub": "", "text": "Trong đồng cỏ xanh tươi, Người cho tôi nằm nghỉ. Người đưa tôi tới dòng nước trong lành"},
            {"num": 3, "sub": "", "text": "và bổ sức cho tôi. Người dẫn tôi trên đường ngay nẻo chính vì danh dự của Người."},
            {"num": 4, "sub": "", "text": "Lạy Chúa, dầu qua lũng nghìn trùng u tối, con không lo sợ sự dữ nào, vì Chúa ở cùng con. Cây roi và chiếc gậy của Ngài, đó là điều an ủi lòng con."},
            {"num": 5, "sub": "", "text": "Chúa dọn sẵn cho con bàn tiệc ngay trước mặt quân thù; đầu con, Chúa xức đượm dầu thơm, ly rượu con đầy tràn chan chứa."},
            {"num": 6, "sub": "", "text": "Lòng nhân hậu và tình thương Chúa ấp ủ tôi suốt cả cuộc đời, và tôi sẽ cư ngụ trong nhà Chúa suốt chuỗi ngày dài triền miên."}
        ]
    },
    {
        "book_code": "Mt",
        "chapter_num": 5,
        "title": "Chương 5",
        "audio_url": "https://augustino.net/wp-content/uploads/audio/Mt-5.mp3",
        "verses": [
            {"num": 1, "section": "BÀI GIẢNG TRÊN NÚI", "sub": "Phúc thật tám mối", "text": "Thấy đám đông, Đức Giêsu lên núi. Người ngồi xuống, các môn đệ đến gần bên."},
            {"num": 2, "sub": "", "text": "Người mở miệng dạy họ rằng:"},
            {"num": 3, "sub": "", "text": "“Phúc thay ai có tâm hồn nghèo khó, vì Nước Trời là của họ."},
            {"num": 4, "sub": "", "text": "Phúc thay ai hiền lành, vì họ sẽ được Đất Hứa làm gia nghiệp."},
            {"num": 5, "sub": "", "text": "Phúc thay ai sầu khổ, vì họ sẽ được Thiên Chúa ủi an."},
            {"num": 6, "sub": "", "text": "Phúc thay ai khát khao nên người công chính, vì họ sẽ được Thiên Chúa cho thỏa lòng."},
            {"num": 7, "sub": "", "text": "Phúc thay ai xót thương người, vì họ sẽ được Thiên Chúa xót thương."},
            {"num": 8, "sub": "", "text": "Phúc thay ai có tâm hồn trong sạch, vì họ sẽ được nhìn thấy Thiên Chúa."},
            {"num": 9, "sub": "", "text": "Phúc thay ai xây dựng hòa bình, vì họ sẽ được gọi là con Thiên Chúa."},
            {"num": 10, "sub": "", "text": "Phúc thay ai bị bách hại vì sống công chính, vì Nước Trời là của họ."},
            {"num": 11, "sub": "", "text": "Phúc thay anh em khi vì Thầy mà bị người ta sỉ vả, bách hại và vu khống đủ điều xấu xa."},
            {"num": 12, "sub": "", "text": "Anh em hãy vui mừng hớn hở, vì phần thưởng dành cho anh em ở trên trời thật lớn lao. Quả vậy, các ngôn sứ là những người đi trước anh em cũng từng bị người ta bách hại như thế."},
            {"num": 13, "sub": "Muối cho đời và ánh sáng cho trần gian", "text": "“Chính anh em là muối cho đời. Nhưng muối mà nhạt đi, thì lấy gì muối nó cho mặn lại? Nó đã thành vô dụng, chỉ còn việc quẳng ra ngoài cho người ta chà đạp thôi."},
            {"num": 14, "sub": "", "text": "Chính anh em là ánh sáng cho trần gian. Một thành xây trên núi không tài nào che giấu được."},
            {"num": 15, "sub": "", "text": "Cũng chẳng có ai thắp đèn rồi lại để dưới cái thùng, nhiều là đặt trên đế, và nó soi sáng cho mọi người trong nhà."},
            {"num": 16, "sub": "", "text": "Cũng vậy, ánh sáng của anh em phải chiếu giãi trước mặt thiên hạ, để họ thấy những công việc tốt đẹp anh em làm, mà tôn vinh Cha của anh em, Đấng ngự trên trời.”"}
        ]
    },
    {
        "book_code": "Ga",
        "chapter_num": 1,
        "title": "Chương 1",
        "audio_url": "https://augustino.net/wp-content/uploads/audio/Ga-1.mp3",
        "verses": [
            {"num": 1, "section": "LỜI TỰA TIN MỪNG", "sub": "Ngôi Lời Nhập Thể", "text": "Lúc khởi đầu đã có Ngôi Lời. Ngôi Lời vẫn hướng về Thiên Chúa, và Ngôi Lời là Thiên Chúa."},
            {"num": 2, "sub": "", "text": "Lúc khởi đầu, Người vẫn hướng về Thiên Chúa."},
            {"num": 3, "sub": "", "text": "Nhờ Người mà vạn vật được tạo thành, và không có Người, thì chẳng có gì được tạo thành."},
            {"num": 4, "sub": "", "text": "Điều đã được tạo thành ở nơi Người là sự sống, và sự sống là ánh sáng cho nhân loại."},
            {"num": 5, "sub": "", "text": "Ánh sáng chiếu soi trong bóng tối, và bóng tối đã không diệt trừ được ánh sáng."},
            {"num": 14, "sub": "", "text": "Ngôi Lời đã trở nên người phàm và cư ngụ giữa chúng ta. Chúng tôi đã được ngắm nhìn vinh quang của Người, vinh quang mà Chúa Cha ban cho Người, là Con Một đầy tràn ân sủng và sự thật."}
        ]
    },
    {
        "book_code": "Ga",
        "chapter_num": 3,
        "title": "Chương 3",
        "audio_url": "https://augustino.net/wp-content/uploads/audio/Ga-3.mp3",
        "verses": [
            {"num": 16, "section": "ĐỨC GIÊSU VÀ ÔNG NICÔĐÊMÔ", "sub": "Tình yêu Thiên Chúa ban Con Một", "text": "Thiên Chúa yêu thế gian đến nỗi đã ban Con Một, để ai tin vào Con của Người thì khỏi phải chết, nhưng được sống muôn đời."},
            {"num": 17, "sub": "", "text": "Quả vậy, Thiên Chúa sai Con của Người đến thế gian, không phải để lên án thế gian, nhưng là để thế gian, nhờ Con của Người, mà được cứu độ."}
        ]
    },
    {
        "book_code": "1Cr",
        "chapter_num": 13,
        "title": "Chương 13",
        "audio_url": "https://augustino.net/wp-content/uploads/audio/1Cr-13.mp3",
        "verses": [
            {"num": 1, "section": "BÀI CA ĐỨC MẾN", "sub": "Đức mến cao trọng tuyệt đối", "text": "Giả như tôi có nói được các thứ tiếng của loài người và của các thiên thần đi nữa, mà không có đức mến, thì tôi cũng chẳng khác gì thanh la vang tiếng, hay thanh la inh ỏi."},
            {"num": 2, "sub": "", "text": "Giả như tôi có được ơn nói tiên tri, và biết hết mọi mầu nhiệm, mọi sự hiểu biết, và giả như tôi có được tất cả đức tin để chuyển núi dời non, mà không có đức mến, thì tôi cũng chẳng là gì."},
            {"num": 3, "sub": "", "text": "Giả như tôi có phân phát hết tài sản của tôi để nuôi người nghèo khó, và giả như tôi có nộp cả thân xác tôi để chịu thiêu đốt, mà không có đức mến, thì cũng chẳng ích gì cho tôi."},
            {"num": 4, "sub": "Đặc tính của Đức Mến", "text": "Đức mến thì nhẫn nhục, hiền hậu, không ghen tương, không vênh vang, không tự đắc,"},
            {"num": 5, "sub": "", "text": "không làm điều bất chính, không tìm tư lợi, không nóng giận, không nuôi hận thù,"},
            {"num": 6, "sub": "", "text": "không mừng khi thấy sự bất công, nhưng vui khi thấy điều chân thật."},
            {"num": 7, "sub": "", "text": "Đức mến tha thứ tất cả, tin tưởng tất cả, hy vọng tất cả, chịu đựng tất cả."},
            {"num": 8, "sub": "", "text": "Đức mến không bao giờ mất được. Ơn nói tiên tri sẽ hết, ơn nói các tiếng lạ sẽ ngưng, sự hiểu biết sẽ qua đi."},
            {"num": 13, "sub": "", "text": "Hiện nay đức tin, đức cậy, đức mến, cả ba đều tồn tại, nhưng cao trọng hơn cả là đức mến."}
        ]
    }
]

class Command(BaseCommand):
    help = "Nạp sẵn văn bản mẫu đầy đủ cho các sách tiêu biểu (Sáng Thế, Thánh Vịnh, Mát-thêu, Gio-an, 1 Cô-rin-tô)"

    def handle(self, *args, **options):
        self.stdout.write("Bắt đầu nạp các chương sách mẫu có văn bản đầy đủ...")
        verses_created = 0

        for item in SAMPLE_DATA:
            try:
                book = Book.objects.get(code=item["book_code"])
            except Book.DoesNotExist:
                self.stderr.write(f"Chưa tìm thấy sách {item['book_code']}, hãy chạy `python manage.py init_canon` trước!")
                return

            chapter, _ = Chapter.objects.get_or_create(
                book=book,
                number=item["chapter_num"],
                defaults={"title": item.get("title", f"Chương {item['chapter_num']}"), "audio_url": item.get("audio_url", "")}
            )
            if item.get("audio_url"):
                chapter.audio_url = item["audio_url"]
                chapter.save()

            for v in item["verses"]:
                verse, created = Verse.objects.update_or_create(
                    chapter=chapter,
                    verse_number=v["num"],
                    defaults={
                        "section_title": v.get("section", ""),
                        "sub_title": v.get("sub", ""),
                        "text": v["text"],
                    }
                )
                verses_created += 1

        self.stdout.write(self.style.SUCCESS(f"-> Đã nạp thành công {verses_created} câu Kinh Thánh mẫu chuẩn đẹp!"))

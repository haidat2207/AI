# ĐỒ ÁN CÁ NHÂN TRÍ TUỆ NHÂN TẠO

Repository này lưu trữ các bài tập, chương trình mô phỏng và mô hình thực hành **cá nhân** trong môn Trí tuệ nhân tạo.

Nội dung bao gồm bài toán 8-Puzzle, mô hình thế giới máy hút bụi, bài toán tô màu bản đồ Thành phố Hồ Chí Minh sau sáp nhập bằng CSP, trò chơi cờ Caro sử dụng thuật toán đối kháng và một số bài tập về agent.

> Đây là repository phục vụ mục đích học tập và thực hành cá nhân.

---

## Cấu trúc thư mục

```text
AI/
│
├── BFS/
├── CSP/
├── CaroChest/
├── MayHutBui/
├── Model_Based_Agent/
├── Simple_Reflex_Agent/
└── README.md
```

---

## Nội dung từng thư mục

### `BFS` – Bài toán 8-Puzzle

Thư mục này chứa chương trình giải bài toán **8-Puzzle** bằng thuật toán tìm kiếm theo chiều rộng **Breadth-First Search (BFS)**.

Bài toán 8-Puzzle gồm 8 ô số và 1 ô trống được đặt trên lưới 3×3. Mỗi lần di chuyển, ô trống có thể đổi vị trí với ô ở trên, dưới, trái hoặc phải. Mục tiêu là đưa trạng thái ban đầu về trạng thái mục tiêu.

Thuật toán BFS duyệt các trạng thái theo từng mức độ sâu. Vì mỗi thao tác đổi ô được xem là có cùng chi phí, BFS có thể tìm được lời giải có số bước di chuyển ít nhất.

Chương trình hỗ trợ:

* Nhập hoặc thiết lập trạng thái ban đầu.
* Xác định trạng thái mục tiêu.
* Tìm đường đi từ trạng thái đầu đến trạng thái đích.
* Hiển thị các bước đổi vị trí của ô trống.
* Thống kê số trạng thái đã xét và thời gian chạy.

---

### `MayHutBui` – Mô hình thế giới máy hút bụi

Thư mục này chứa các chương trình mô phỏng robot máy hút bụi hoạt động trong môi trường dạng lưới.

Robot có nhiệm vụ di chuyển, quan sát môi trường và làm sạch các ô có rác. Mô hình được sử dụng để minh họa cách agent nhận biết trạng thái môi trường, lựa chọn hành động và đạt trạng thái mục tiêu là môi trường sạch.

Các nội dung có thể bao gồm:

* Tìm kiếm không có thông tin.
* Tìm kiếm có thông tin.
* Tìm kiếm cục bộ.
* Tìm kiếm trong môi trường không quan sát được hoặc quan sát một phần.
* So sánh đường đi, số trạng thái xét, chi phí và thời gian chạy.

---

### `CSP` – Tô màu bản đồ Thành phố Hồ Chí Minh sau sáp nhập

Thư mục này chứa bài toán tô màu bản đồ Thành phố Hồ Chí Minh sau sáp nhập dưới dạng bài toán thỏa mãn ràng buộc (**Constraint Satisfaction Problem – CSP**).

Mục tiêu của bài toán là gán màu cho các khu vực trên bản đồ sao cho hai khu vực liền kề không sử dụng cùng một màu.

Bài toán được mô hình hóa như sau:

* **Biến:** các khu vực hoặc đơn vị hành chính trên bản đồ.
* **Miền giá trị:** các màu có thể sử dụng.
* **Ràng buộc:** hai khu vực kề nhau phải có màu khác nhau.

Các thuật toán CSP được áp dụng:

* Backtracking.
* Forward Checking.
* AC-3 kết hợp Backtracking.
* Min-Conflicts.

Chương trình có phần trực quan hóa quá trình gán màu, kiểm tra ràng buộc, thu hẹp miền giá trị, quay lui và giải quyết xung đột.

---

### `CaroChest` – Trò chơi cờ Caro

Thư mục này chứa trò chơi cờ Caro giữa người chơi và máy tính.

Máy tính sử dụng các thuật toán tìm kiếm đối kháng để đánh giá trạng thái bàn cờ và lựa chọn nước đi phù hợp.

Các thuật toán được áp dụng gồm:

* **Minimax:** xét các nước đi có thể xảy ra của hai người chơi để chọn nước đi tốt nhất.
* **Alpha-Beta Pruning:** cải tiến Minimax bằng cách cắt tỉa các nhánh không cần xét.
* **Expectimax:** đánh giá nước đi dựa trên giá trị kỳ vọng trong các tình huống có yếu tố ngẫu nhiên.

Chương trình hỗ trợ người chơi tương tác với máy, lựa chọn thuật toán AI và quan sát kết quả thắng, thua hoặc hòa.

---

### `Model_Based_Agent` – Agent dựa trên mô hình

Thư mục này chứa mô hình **Model-Based Agent**.

Khác với Simple Reflex Agent, agent dạng này không chỉ dựa vào trạng thái đang quan sát được mà còn lưu lại thông tin về trạng thái trước đó và mô hình môi trường bên trong.

Agent sử dụng thông tin đã lưu để suy luận về môi trường hiện tại, từ đó chọn hành động phù hợp hơn trong trường hợp không thể quan sát toàn bộ môi trường.

---

### `Simple_Reflex_Agent` – Agent phản xạ đơn giản

Thư mục này chứa mô hình **Simple Reflex Agent**.

Agent lựa chọn hành động trực tiếp dựa trên trạng thái hiện tại thông qua các luật điều kiện – hành động.

Ví dụ:

```text
Nếu ô hiện tại có rác → Hút bụi
Nếu ô hiện tại sạch → Di chuyển sang ô khác
```

Mô hình này phù hợp với môi trường đơn giản, nơi agent có thể quan sát đầy đủ trạng thái cần thiết để đưa ra quyết định.

---

## Mục tiêu thực hiện

* Hiểu nguyên lý hoạt động của các nhóm thuật toán trong Trí tuệ nhân tạo.
* Áp dụng các thuật toán vào những bài toán mô phỏng cụ thể.
* Trực quan hóa quá trình agent tìm kiếm, suy luận và đưa ra quyết định.
* So sánh kết quả giữa các thuật toán thông qua số bước, chi phí, số trạng thái đã xét và thời gian chạy.
* Rèn luyện kỹ năng lập trình Python và xây dựng giao diện mô phỏng thuật toán.

---

## Công nghệ sử dụng

* Python
* Tkinter
* Jupyter Notebook
* JSON / GeoJSON
* Các thư viện Python hỗ trợ mô phỏng và trực quan hóa

---

## Cách chạy chương trình

Clone repository về máy:

```bash
git clone <link-repository>
```

Di chuyển vào thư mục repository:

```bash
cd AI
```

Sau đó chọn thư mục bài tập muốn chạy, ví dụ:

```bash
cd BFS
```

Chạy file Python chính:

```bash
python main.py
```

Một số bài có thể có file chạy chính với tên khác hoặc sử dụng Jupyter Notebook `.ipynb`. Khi đó, mở đúng file trong Visual Studio Code hoặc Jupyter Notebook để thực hiện.

---

## Ghi chú

Mỗi thư mục là một bài tập hoặc mô hình riêng nên cấu trúc file và cách chạy có thể khác nhau. Người dùng nên xem các file Python hoặc Notebook bên trong từng thư mục để xác định file chương trình chính.

---

## Tác giả

* Sinh viên: Hải Đạt
* Nội dung: Đồ án cá nhân môn Trí tuệ nhân tạo

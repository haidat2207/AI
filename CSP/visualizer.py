import json
import math
import os
import tkinter as tk
from tkinter import ttk, messagebox

from backtracking import solve_map_coloring as solve_backtracking
from forwardchecking import solve_map_coloring as solve_forwardchecking


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WARDS_PATH = os.path.join(BASE_DIR, "Wards.json")
PROVINCE_PATH = os.path.join(BASE_DIR, "provNew.geojson")

COLORS = ["Đỏ", "Xanh lá", "Xanh dương", "Vàng"]
COLOR_HEX = {
    "Đỏ": "#ff6b6b",
    "Xanh lá": "#69db7c",
    "Xanh dương": "#74c0fc",
    "Vàng": "#ffd43b",
}

DEFAULT_FILL = "#f8f9fa"
SEA_FILL = "#e7f5ff"
LAND_FILL = "#fff9db"
NORMAL_OUTLINE = "#6f42c1"
OUTER_OUTLINE = "#212529"
CURRENT_OUTLINE = "#111827"
REJECT_OUTLINE = "#d00000"
TEXT_COLOR = "#212529"



def topo_arc_index(ref):
    """TopoJSON: ref âm nghĩa là đảo chiều arc theo ~ref = -ref - 1."""
    return ref if ref >= 0 else -ref - 1


def get_arc_points(arcs, ref):
    idx = topo_arc_index(ref)
    pts = arcs[idx]
    if ref < 0:
        pts = list(reversed(pts))
    return pts


def build_ring(arcs, refs):
    """
    Ghép nhiều arc thành 1 ring.
    Tránh lặp điểm đầu/cuối khi nối arc.
    """
    ring = []
    for ref in refs:
        pts = get_arc_points(arcs, ref)
        if not pts:
            continue

        if ring and ring[-1] == pts[0]:
            ring.extend(pts[1:])
        else:
            ring.extend(pts)

    return ring


def geometry_to_rings(geometry, arcs):
    """
    Trả về list polygon.
    Mỗi polygon là list ring.
    ring đầu là viền ngoài; các ring sau nếu có là lỗ/đảo phụ.
    """
    gtype = geometry.get("type")
    arc_data = geometry.get("arcs", [])

    if gtype == "Polygon":
        return [[build_ring(arcs, ring_refs) for ring_refs in arc_data]]

    if gtype == "MultiPolygon":
        polygons = []
        for polygon_refs in arc_data:
            polygons.append([build_ring(arcs, ring_refs) for ring_refs in polygon_refs])
        return polygons

    return []


def collect_arc_refs(obj):
    """
    Lấy tất cả arc id tuyệt đối trong cấu trúc arcs của Polygon/MultiPolygon.
    Dùng để suy ra quan hệ kề nhau: 2 vùng cùng dùng 1 arc => kề nhau.
    """
    if isinstance(obj, int):
        yield topo_arc_index(obj)
    elif isinstance(obj, list):
        for item in obj:
            yield from collect_arc_refs(item)


def ring_area(points):
    if len(points) < 3:
        return 0

    area = 0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        area += x1 * y2 - x2 * y1

    return area / 2


def ring_centroid(points):
    """
    Centroid của polygon theo công thức shoelace.
    Nếu polygon quá nhỏ/lỗi thì dùng trung bình điểm.
    """
    if len(points) < 3:
        if not points:
            return 0, 0
        return sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)

    area2 = 0
    cx = 0
    cy = 0

    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        cross = x1 * y2 - x2 * y1
        area2 += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross

    if abs(area2) < 1e-12:
        return sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)

    return cx / (3 * area2), cy / (3 * area2)


def bbox_of_points(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def bbox_union(bboxes):
    return (
        min(b[0] for b in bboxes),
        min(b[1] for b in bboxes),
        max(b[2] for b in bboxes),
        max(b[3] for b in bboxes),
    )


def polygon_bbox(polygons):
    boxes = []
    for polygon in polygons:
        for ring in polygon:
            if ring:
                boxes.append(bbox_of_points(ring))
    return bbox_union(boxes)


def largest_ring(polygons):
    best = []
    best_area = -1
    for polygon in polygons:
        for ring in polygon:
            area = abs(ring_area(ring))
            if area > best_area:
                best_area = area
                best = ring
    return best


def load_wards_topology(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("type") != "Topology":
        raise ValueError("Wards.json phải là TopoJSON type=Topology")

    arcs = data["arcs"]
    geometries = data["objects"]["collection"]["geometries"]

    regions = {}
    arc_to_regions = {}

    for geom in geometries:
        props = geom.get("properties", {})
        name = props.get("Tên") or props.get("Ten") or f"Vùng {len(regions) + 1}"
        stt = props.get("STT", len(regions) + 1)
        polygons = geometry_to_rings(geom, arcs)
        bbox = polygon_bbox(polygons)
        centroid = ring_centroid(largest_ring(polygons))

        regions[name] = {
            "name": name,
            "stt": stt,
            "type": geom.get("type"),
            "polygons": polygons,
            "bbox": bbox,
            "centroid": centroid,
            "arc_refs": set(collect_arc_refs(geom.get("arcs", []))),
        }

        for arc_id in regions[name]["arc_refs"]:
            arc_to_regions.setdefault(arc_id, set()).add(name)

    neighbors = {name: set() for name in regions}
    for names in arc_to_regions.values():
        if len(names) >= 2:
            names = list(names)
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a = names[i]
                    b = names[j]
                    neighbors[a].add(b)
                    neighbors[b].add(a)

    neighbors = {name: sorted(list(values)) for name, values in neighbors.items()}
    return regions, neighbors


def load_province_outline(path):
    """
    Đọc provNew.geojson để lấy viền ngoài TP HCM.
    Nếu thiếu file vẫn chạy được, vì Wards.json đã đủ ranh giới phường/xã.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    outlines = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        name = str(props.get("Tỉnh thành mới", ""))
        if name.strip().upper().replace(".", "") not in {"TP HCM", "TPHCM", "THÀNH PHỐ HỒ CHÍ MINH"}:
            continue

        geom = feature.get("geometry", {})
        gtype = geom.get("type")
        coords = geom.get("coordinates", [])

        if gtype == "Polygon":
            for ring in coords:
                outlines.append(ring)
        elif gtype == "MultiPolygon":
            for polygon in coords:
                for ring in polygon:
                    outlines.append(ring)

    return outlines


class GeoProjector:
    def __init__(self, bbox, rect):
        self.minx, self.miny, self.maxx, self.maxy = bbox
        self.x0, self.y0, self.x1, self.y1 = rect

        bw = self.maxx - self.minx
        bh = self.maxy - self.miny
        rw = self.x1 - self.x0
        rh = self.y1 - self.y0

        if bw == 0 or bh == 0:
            self.scale = 1
            self.dx = self.x0
            self.dy = self.y0
            return

        self.scale = min(rw / bw, rh / bh)
        used_w = bw * self.scale
        used_h = bh * self.scale
        self.dx = self.x0 + (rw - used_w) / 2
        self.dy = self.y0 + (rh - used_h) / 2

    def project(self, lon, lat):
        x = self.dx + (lon - self.minx) * self.scale
        # Canvas y tăng xuống dưới nên phải đảo trục lat
        y = self.dy + (self.maxy - lat) * self.scale
        return x, y

    def project_flat(self, points):
        flat = []
        for lon, lat in points:
            x, y = self.project(lon, lat)
            flat.extend([x, y])
        return flat


class MapColoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Map Coloring Visualizer - TP.HCM sau sáp nhập bằng ranh giới thật")
        self.root.geometry("1500x900")
        self.root.minsize(1250, 780)

        self.regions, self.neighbors = load_wards_topology(WARDS_PATH)
        self.province_outlines = load_province_outline(PROVINCE_PATH)

        # Sắp xếp vùng theo độ khó để thuật toán chạy mượt hơn
        self.variables = sorted(
            self.regions.keys(),
            key=lambda name: (-len(self.neighbors.get(name, [])), self.regions[name]["stt"])
        )

        self.algorithm_var = tk.StringVar(value="Forward Checking")
        self.speed_var = tk.IntVar(value=80)
        self.label_mode_var = tk.StringVar(value="stt")  # none/stt/name

        self.generator = None
        self.is_running = False
        self.step_no = 0

        self.region_items = {name: [] for name in self.regions}
        self.region_label_items = {}
        self.status_rows = {}
        self.item_to_region = {}

        self.main_projector = None
        self.island_projector = None
        self.main_bbox = None
        self.island_bbox = None

        self.current_info_var = tk.StringVar(value="Đưa chuột lên vùng để xem tên.")
        self.summary_var = tk.StringVar()

        self.create_layout()
        self.prepare_projectors()
        self.draw_map()
        self.reset_all()

    def create_layout(self):
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = ttk.Frame(main, width=470)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right.pack_propagate(False)

        title = ttk.Label(
            left,
            text="CSP - Tô màu bản đồ TP.HCM sau sáp nhập",
            font=("Arial", 16, "bold"),
        )
        title.pack(anchor="w")

        note = ttk.Label(
            left,
            textvariable=self.summary_var,
            font=("Arial", 10),
        )
        note.pack(anchor="w", pady=(2, 6))

        canvas_frame = ttk.Frame(left)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=1000,
            height=820,
            bg=SEA_FILL,
            highlightthickness=1,
            highlightbackground="#868e96",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        vbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        hbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")

        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        self.canvas.configure(scrollregion=(0, 0, 1120, 940))

        info = ttk.Label(left, textvariable=self.current_info_var, font=("Arial", 10, "bold"))
        info.pack(anchor="w", pady=(6, 0))

        control_box = ttk.LabelFrame(right, text="Điều khiển", padding=10)
        control_box.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(control_box, text="Thuật toán:").grid(row=0, column=0, sticky="w")
        algo = ttk.Combobox(
            control_box,
            textvariable=self.algorithm_var,
            values=["Backtracking", "Forward Checking"],
            state="readonly",
        )
        algo.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(control_box, text="Tốc độ:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        speed = ttk.Scale(control_box, from_=800, to=10, variable=self.speed_var, orient=tk.HORIZONTAL)
        speed.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))

        ttk.Label(control_box, text="Hiện nhãn:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        label_box = ttk.Combobox(
            control_box,
            textvariable=self.label_mode_var,
            values=["none", "stt", "name"],
            state="readonly",
        )
        label_box.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))
        label_box.bind("<<ComboboxSelected>>", lambda e: self.redraw_labels())

        btn_row = ttk.Frame(control_box)
        btn_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.run_btn = ttk.Button(btn_row, text="Chạy", command=self.run_algorithm)
        self.run_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        self.step_btn = ttk.Button(btn_row, text="Từng bước", command=self.step_algorithm)
        self.step_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

        self.reset_btn = ttk.Button(btn_row, text="Reset", command=self.reset_all)
        self.reset_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

        control_box.columnconfigure(1, weight=1)

        legend = ttk.LabelFrame(right, text="Màu sử dụng", padding=8)
        legend.pack(fill=tk.X, pady=(0, 8))

        for color_name in COLORS:
            row = ttk.Frame(legend)
            row.pack(fill=tk.X, pady=2)
            swatch = tk.Canvas(row, width=24, height=16, highlightthickness=1, highlightbackground="#555")
            swatch.create_rectangle(0, 0, 24, 16, fill=COLOR_HEX[color_name], outline="")
            swatch.pack(side=tk.LEFT)
            ttk.Label(row, text=color_name).pack(side=tk.LEFT, padx=8)

        status_box = ttk.LabelFrame(right, text="Bảng trạng thái màu", padding=8)
        status_box.pack(fill=tk.BOTH, expand=False, pady=(0, 8))

        status_frame = ttk.Frame(status_box)
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.status_tree = ttk.Treeview(
            status_frame,
            columns=("stt", "region", "color", "deg"),
            show="headings",
            height=11,
        )
        self.status_tree.heading("stt", text="STT")
        self.status_tree.heading("region", text="Tên vùng")
        self.status_tree.heading("color", text="Màu")
        self.status_tree.heading("deg", text="Kề")
        self.status_tree.column("stt", width=45, anchor="center", stretch=False)
        self.status_tree.column("region", width=190, anchor="w")
        self.status_tree.column("color", width=70, anchor="center")
        self.status_tree.column("deg", width=45, anchor="center", stretch=False)
        self.status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        status_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_tree.yview)
        status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_tree.configure(yscrollcommand=status_scroll.set)
        self.status_tree.bind("<<TreeviewSelect>>", self.on_status_select)

        domain_box = ttk.LabelFrame(right, text="Miền màu còn lại / vùng đang xét", padding=8)
        domain_box.pack(fill=tk.X, pady=(0, 8))

        self.domain_text = tk.Text(domain_box, height=6, wrap=tk.WORD, font=("Consolas", 9))
        self.domain_text.pack(fill=tk.X)
        self.domain_text.configure(state=tk.DISABLED)

        log_box = ttk.LabelFrame(right, text="Bảng hành động thực hiện", padding=8)
        log_box.pack(fill=tk.BOTH, expand=True)

        log_frame = ttk.Frame(log_box)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_tree = ttk.Treeview(log_frame, columns=("step", "action"), show="headings")
        self.log_tree.heading("step", text="Bước")
        self.log_tree.heading("action", text="Hành động")
        self.log_tree.column("step", width=55, anchor="center", stretch=False)
        self.log_tree.column("action", width=350, anchor="w")
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_tree.configure(yscrollcommand=log_scroll.set)

    def prepare_projectors(self):
        mainland_boxes = []
        island_boxes = []

        for name, info in self.regions.items():
            if name == "Côn Đảo":
                island_boxes.append(info["bbox"])
            else:
                mainland_boxes.append(info["bbox"])

        self.main_bbox = bbox_union(mainland_boxes)
        self.island_bbox = bbox_union(island_boxes) if island_boxes else self.main_bbox

        self.main_rect = (35, 70, 850, 885)
        self.island_rect = (880, 650, 1080, 840)

        self.main_projector = GeoProjector(self.main_bbox, self.main_rect)
        self.island_projector = GeoProjector(self.island_bbox, self.island_rect)

        total = len(self.regions)
        self.summary_var.set(
            "CSP - Map Coloring Problem: các vùng kề nhau không được trùng màu."
        )

    def get_projector_for_region(self, name):
        return self.island_projector if name == "Côn Đảo" else self.main_projector

    def get_projector_for_ring(self, ring):
        # Nếu phần lớn điểm ở vĩ độ thấp dưới 9.5 thì đưa vào inset Côn Đảo
        if not ring:
            return self.main_projector
        avg_lat = sum(p[1] for p in ring) / len(ring)
        return self.island_projector if avg_lat < 9.5 else self.main_projector

    def draw_map(self):
        self.canvas.delete("all")
        self.region_items = {name: [] for name in self.regions}
        self.region_label_items = {}
        self.item_to_region = {}

        self.draw_background()
        self.draw_regions()
        self.draw_outer_outline()
        self.redraw_labels()
        self.bind_canvas_events()

    def draw_background(self):
        self.canvas.create_rectangle(0, 0, 1120, 940, fill=SEA_FILL, outline="")

        # Nền đất bản đồ chính
        self.canvas.create_rectangle(
            self.main_rect[0] - 15, self.main_rect[1] - 15,
            self.main_rect[2] + 15, self.main_rect[3] + 15,
            fill=LAND_FILL,
            outline="#adb5bd",
            width=1,
        )

        for x in range(40, 860, 80):
            self.canvas.create_line(x, 70, x, 885, fill="#d0ebff", width=1)
        for y in range(80, 885, 80):
            self.canvas.create_line(35, y, 850, y, fill="#d0ebff", width=1)

        self.canvas.create_text(
            560, 26,
            text="BẢN ĐỒ PHƯỜNG/XÃ TP.HỒ CHÍ MINH SAU SÁP NHẬP",
            font=("Arial", 15, "bold"),
            fill=TEXT_COLOR,
        )
        self.canvas.create_text(
            560, 48,
            text="CSP - Map Coloring Problem",
            font=("Arial", 10),
            fill="#495057",
        )

        labels = [
            (42, 105, "TÂY NINH"),
            (38, 575, "LONG AN"),
            (855, 120, "ĐỒNG NAI"),
            (855, 455, "BÌNH THUẬN"),
            (780, 890, "BIỂN ĐÔNG"),
        ]
        for x, y, text in labels:
            self.canvas.create_text(x, y, text=text, anchor="w", font=("Arial", 10, "bold"), fill="#495057")

        # Mũi tên Bắc
        self.canvas.create_line(1045, 85, 1045, 145, arrow=tk.FIRST, width=2, fill="#343a40")
        self.canvas.create_text(1045, 65, text="B", font=("Arial", 13, "bold"), fill="#343a40")

        # Tỉ lệ mô phỏng
        self.canvas.create_line(910, 95, 1010, 95, fill="#343a40", width=3)
        self.canvas.create_line(910, 88, 910, 102, fill="#343a40", width=2)
        self.canvas.create_line(1010, 88, 1010, 102, fill="#343a40", width=2)
        self.canvas.create_text(960, 80, text="0        40 km", font=("Arial", 9), fill="#343a40")

        # Khung Côn Đảo
        self.canvas.create_rectangle(
            self.island_rect[0] - 18, self.island_rect[1] - 42,
            self.island_rect[2] + 18, self.island_rect[3] + 45,
            fill="#f8f9fa",
            outline="#868e96",
            width=2,
        )
        self.canvas.create_text(
            (self.island_rect[0] + self.island_rect[2]) / 2,
            self.island_rect[1] - 24,
            text="ĐẶC KHU CÔN ĐẢO",
            font=("Arial", 10, "bold"),
            fill=TEXT_COLOR,
        )

    def draw_regions(self):
        for name, info in self.regions.items():
            projector = self.get_projector_for_region(name)

            for polygon in info["polygons"]:
                for ring_index, ring in enumerate(polygon):
                    if len(ring) < 3:
                        continue

                    flat = projector.project_flat(ring)

                    # Canvas không cắt lỗ polygon, nên cứ vẽ ring thành mảng riêng.
                    item = self.canvas.create_polygon(
                        flat,
                        fill=DEFAULT_FILL,
                        outline=NORMAL_OUTLINE,
                        width=1,
                        tags=("region",)
                    )
                    self.region_items[name].append(item)
                    self.item_to_region[item] = name

        # Tăng độ đậm viền vùng ngoài sau khi vẽ xong
        for items in self.region_items.values():
            for item in items:
                self.canvas.tag_raise(item)

    def draw_outer_outline(self):
        if not self.province_outlines:
            return

        for ring in self.province_outlines:
            if len(ring) < 2:
                continue

            projector = self.get_projector_for_ring(ring)
            flat = projector.project_flat(ring)

            # Vẽ line qua các điểm và khép kín
            if len(flat) >= 4:
                flat_closed = flat[:]
                flat_closed.extend(flat[:2])
                self.canvas.create_line(
                    flat_closed,
                    fill=OUTER_OUTLINE,
                    width=2.5,
                    smooth=False,
                )

    def redraw_labels(self):
        for item in self.region_label_items.values():
            self.canvas.delete(item)
        self.region_label_items = {}

        mode = self.label_mode_var.get()
        if mode == "none":
            return

        for name, info in self.regions.items():
            projector = self.get_projector_for_region(name)
            lon, lat = info["centroid"]
            x, y = projector.project(lon, lat)

            text = str(info["stt"]) if mode == "stt" else name

            # Tên vùng thật nhiều nên font nhỏ; có thể đổi sang STT cho dễ nhìn.
            font_size = 5 if mode == "name" else 6
            label = self.canvas.create_text(
                x, y,
                text=text,
                font=("Arial", font_size, "bold"),
                fill="#111111",
                justify=tk.CENTER,
                width=60 if mode == "name" else 24,
            )
            self.region_label_items[name] = label

        self.raise_labels()

    def raise_labels(self):
        for item in self.region_label_items.values():
            self.canvas.tag_raise(item)

    def bind_canvas_events(self):
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Leave>", lambda e: self.current_info_var.set("Đưa chuột lên vùng để xem tên."))

    def on_canvas_motion(self, event):
        current = self.canvas.find_withtag("current")
        if not current:
            return

        item = current[0]
        name = self.item_to_region.get(item)
        if not name:
            return

        info = self.regions[name]
        deg = len(self.neighbors.get(name, []))
        self.current_info_var.set(
            f"{info['stt']}. {name} | Số vùng kề: {deg} | Kề: {', '.join(self.neighbors.get(name, [])[:8])}"
        )

    def on_status_select(self, event):
        selected = self.status_tree.selection()
        if not selected:
            return

        values = self.status_tree.item(selected[0], "values")
        if len(values) < 2:
            return

        name = values[1]
        if name in self.regions:
            self.highlight_region(name)
            info = self.regions[name]
            self.current_info_var.set(f"Đang chọn: {info['stt']}. {name}")

    # ============================================================
    # CHẠY THUẬT TOÁN
    # ============================================================

    def create_generator(self):
        algorithm = self.algorithm_var.get()
        if algorithm == "Backtracking":
            return solve_backtracking(self.variables, COLORS, self.neighbors)
        return solve_forwardchecking(self.variables, COLORS, self.neighbors)

    def prepare_new_run(self):
        self.generator = self.create_generator()
        self.step_no = 0
        self.clear_log()
        self.reset_map_colors()
        self.update_status_table({})
        self.update_domain_text({v: COLORS[:] for v in self.variables}, None)

    def run_algorithm(self):
        if self.generator is None:
            self.prepare_new_run()

        self.is_running = True
        self.run_btn.config(state=tk.DISABLED)
        self.step_btn.config(state=tk.DISABLED)
        self.execute_next_step(auto=True)

    def step_algorithm(self):
        if self.generator is None:
            self.prepare_new_run()

        self.execute_next_step(auto=False)

    def execute_next_step(self, auto=False):
        try:
            step = next(self.generator)
        except StopIteration:
            self.finish_run()
            return

        self.apply_step(step)

        if auto and self.is_running:
            self.root.after(int(self.speed_var.get()), lambda: self.execute_next_step(auto=True))

    def finish_run(self):
        self.is_running = False
        self.generator = None
        self.run_btn.config(state=tk.NORMAL)
        self.step_btn.config(state=tk.NORMAL)

    def reset_all(self):
        self.is_running = False
        self.generator = None
        self.step_no = 0
        self.run_btn.config(state=tk.NORMAL)
        self.step_btn.config(state=tk.NORMAL)
        self.clear_log()
        self.reset_map_colors()
        self.update_status_table({})
        self.update_domain_text({v: COLORS[:] for v in self.variables}, None)

    # ============================================================
    # CẬP NHẬT GIAO DIỆN THEO STEP
    # ============================================================

    def reset_map_colors(self):
        for name, items in self.region_items.items():
            for item in items:
                self.canvas.itemconfig(
                    item,
                    fill=DEFAULT_FILL,
                    outline=NORMAL_OUTLINE,
                    width=1,
                )
        self.raise_labels()

    def paint_assignment(self, assignment):
        for name, items in self.region_items.items():
            if name in assignment:
                fill = COLOR_HEX[assignment[name]]
            else:
                fill = DEFAULT_FILL

            for item in items:
                self.canvas.itemconfig(
                    item,
                    fill=fill,
                    outline=NORMAL_OUTLINE,
                    width=1,
                )

        self.raise_labels()

    def highlight_region(self, name, candidate_color=None, rejected=False):
        if name not in self.region_items:
            return

        for item in self.region_items[name]:
            kwargs = {
                "outline": REJECT_OUTLINE if rejected else CURRENT_OUTLINE,
                "width": 3,
            }
            if candidate_color:
                kwargs["fill"] = COLOR_HEX[candidate_color]

            self.canvas.itemconfig(item, **kwargs)

        self.raise_labels()

    def apply_step(self, step):
        self.step_no += 1

        status = step.get("status")
        message = step.get("message", "")
        assignment = step.get("assignment", {})
        domains = step.get("domains")
        current_var = step.get("current_var")
        current_color = step.get("current_color")

        self.paint_assignment(assignment)
        self.add_log(message)
        self.update_status_table(assignment)

        if domains is not None:
            self.update_domain_text(domains, current_var)
        elif status == "start":
            self.update_domain_text({v: COLORS[:] for v in self.variables}, current_var)

        if status == "try" and current_var and current_color:
            self.highlight_region(current_var, current_color, rejected=False)
        elif status == "reject" and current_var:
            self.highlight_region(current_var, current_color, rejected=True)
        elif current_var:
            self.highlight_region(current_var)

        if current_var:
            self.current_info_var.set(f"Bước {self.step_no}: {current_var} - {message}")

        if status == "done":
            self.add_log("Kết quả cuối cùng đã được tô trên bản đồ.")
            self.finish_run()
        elif status == "no_solution":
            self.finish_run()

    def clear_log(self):
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

    def add_log(self, message):
        self.log_tree.insert("", tk.END, values=(self.step_no, message))
        children = self.log_tree.get_children()
        if children:
            self.log_tree.see(children[-1])

    def update_status_table(self, assignment):
        if not self.status_rows:
            # Sắp xếp bảng theo STT hành chính để dễ dò với bản đồ.
            for name in sorted(self.regions.keys(), key=lambda n: self.regions[n]["stt"]):
                info = self.regions[name]
                row = self.status_tree.insert(
                    "",
                    tk.END,
                    values=(info["stt"], name, "Chưa tô", len(self.neighbors.get(name, [])))
                )
                self.status_rows[name] = row

        for name, row_id in self.status_rows.items():
            info = self.regions[name]
            color = assignment.get(name, "Chưa tô")
            self.status_tree.item(
                row_id,
                values=(info["stt"], name, color, len(self.neighbors.get(name, [])))
            )

    def update_domain_text(self, domains, current_var):
        self.domain_text.config(state=tk.NORMAL)
        self.domain_text.delete("1.0", tk.END)

        if current_var:
            self.domain_text.insert(tk.END, f"Đang xét: {current_var}\n")
            self.domain_text.insert(tk.END, f"Miền màu: {', '.join(domains.get(current_var, COLORS))}\n")
            self.domain_text.insert(tk.END, f"Kề: {', '.join(self.neighbors.get(current_var, []))}\n")
        else:
            self.domain_text.insert(tk.END, "Chưa chọn vùng.\n")

        self.domain_text.insert(tk.END, "\nMột số vùng có miền màu ít nhất:\n")
        preview = sorted(
            domains.items(),
            key=lambda kv: (len(kv[1]), kv[0])
        )[:12]

        for name, values in preview:
            self.domain_text.insert(tk.END, f"{name}: {', '.join(values)}\n")

        self.domain_text.config(state=tk.DISABLED)


def main():
    try:
        root = tk.Tk()
        MapColoringApp(root)
        root.mainloop()
    except Exception as exc:
        messagebox.showerror("Lỗi", str(exc))


if __name__ == "__main__":
    main()

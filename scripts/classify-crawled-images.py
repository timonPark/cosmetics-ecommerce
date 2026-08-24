"""
classify-crawled-images.py

미샤 크롤링 이미지를 상품 이미지 / 상세 이미지로 분류하고 파일명을 변경합니다.

분류 기준:
  - 상품 이미지 (product): 500x500 또는 600x600 픽셀 → product_001.jpg, product_002.jpg ...
  - 상세 이미지 (detail): 그 외 모든 크기     → detail_001.jpg, detail_002.jpg ...

실행 방법:
  python3 scripts/classify-crawled-images.py

출력:
  - 이미지 파일명 변경 (in-place)
  - manifest_classified.json  (url, meta_source, description, brand 제거 + 새 파일명 반영)
  - products_classified.csv   (url, description, brand 제거 + product/detail 이미지 수 분리)
"""

import csv
import json
import os
import struct

CRAWL_DIR = "/Users/2309-n0018/PycharmProjects/WelcomeScreen/missha_skincare_images"
MANIFEST_IN = os.path.join(CRAWL_DIR, "manifest.json")
MANIFEST_OUT = os.path.join(CRAWL_DIR, "manifest_classified.json")
CSV_OUT = os.path.join(CRAWL_DIR, "products_classified.csv")

PRODUCT_SIZES: set[tuple[int, int]] = {(500, 500), (600, 600)}

REMOVE_FIELDS = {"url", "meta_source", "description", "brand"}


def get_image_size(path: str) -> tuple[int, int] | tuple[None, None]:
    """확장자 대신 매직 바이트로 실제 포맷을 판별해 크기를 반환."""
    SOF_MARKERS = {
        0xFFC0, 0xFFC1, 0xFFC2, 0xFFC3, 0xFFC5, 0xFFC6, 0xFFC7,
        0xFFC9, 0xFFCA, 0xFFCB, 0xFFCD, 0xFFCE, 0xFFCF,
    }
    NO_LENGTH_MARKERS = {
        0xFFD0, 0xFFD1, 0xFFD2, 0xFFD3, 0xFFD4, 0xFFD5, 0xFFD6, 0xFFD7,
        0xFFD8, 0xFFD9,
    }
    try:
        with open(path, "rb") as f:
            magic = f.read(4)

        if magic[:4] == b"\x89PNG":
            with open(path, "rb") as f:
                f.read(16)
                w, h = struct.unpack(">II", f.read(8))
            return w, h

        if magic[:3] == b"GIF":
            with open(path, "rb") as f:
                f.read(6)
                w, h = struct.unpack("<HH", f.read(4))
            return w, h

        if magic[:2] == b"\xff\xd8":
            with open(path, "rb") as f:
                data = f.read()
            i = 2
            while i < len(data) - 4:
                if data[i] != 0xFF:
                    i += 1
                    continue
                while i < len(data) and data[i] == 0xFF:
                    i += 1
                if i >= len(data):
                    break
                marker = 0xFF00 | data[i]
                i += 1
                if marker in NO_LENGTH_MARKERS or marker == 0xFF00:
                    continue
                if i + 2 > len(data):
                    break
                length = struct.unpack(">H", data[i : i + 2])[0]
                if marker in SOF_MARKERS and i + 7 <= len(data):
                    h, w = struct.unpack(">HH", data[i + 3 : i + 7])
                    return w, h
                i += length

    except Exception:
        return None, None
    return None, None


def is_valid_image(path: str) -> bool:
    """크롤링 실패로 저장된 HTTP 오류 페이지(.jpg 확장자이지만 HTML 내용)를 걸러낸다."""
    try:
        with open(path, "rb") as f:
            magic = f.read(4)
        # HTTP 오류 페이지는 \r\n 으로 시작함
        return magic[:2] != b"\x0d\x0a"
    except Exception:
        return False


def classify_image(path: str) -> str:
    w, h = get_image_size(path)
    if w is None:
        return "detail"
    return "product" if (w, h) in PRODUCT_SIZES else "detail"


def rename_images_in_folder(folder_path: str) -> dict[str, str]:
    """폴더 내 이미지를 분류 후 rename. {기존 파일명: 새 파일명} 반환. 오류 파일은 제외."""
    files = sorted(
        f for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in (".jpg", ".jpeg", ".png", ".gif")
        and is_valid_image(os.path.join(folder_path, f))
    )

    classified: list[tuple[str, str]] = []
    for fname in files:
        kind = classify_image(os.path.join(folder_path, fname))
        classified.append((fname, kind))

    product_idx = 1
    detail_idx = 1
    rename_map: dict[str, str] = {}

    for fname, kind in classified:
        ext = os.path.splitext(fname)[1].lower()
        if kind == "product":
            new_name = f"product_{product_idx:03d}{ext}"
            product_idx += 1
        else:
            new_name = f"detail_{detail_idx:03d}{ext}"
            detail_idx += 1
        rename_map[fname] = new_name

    # 충돌 방지: 임시 이름으로 먼저 rename 후 최종 이름으로 변경
    temp_map: dict[str, str] = {}
    for old, new in rename_map.items():
        temp = f"__tmp_{old}"
        os.rename(
            os.path.join(folder_path, old),
            os.path.join(folder_path, temp),
        )
        temp_map[temp] = new

    for temp, new in temp_map.items():
        os.rename(
            os.path.join(folder_path, temp),
            os.path.join(folder_path, new),
        )

    return rename_map


def build_new_image_path(old_path: str, rename_map: dict[str, str]) -> str:
    """manifest의 기존 이미지 경로를 새 파일명으로 교체."""
    dirname = os.path.dirname(old_path)
    old_fname = os.path.basename(old_path)
    new_fname = rename_map.get(old_fname, old_fname)
    return os.path.join(dirname, new_fname)


def main() -> None:
    with open(MANIFEST_IN, encoding="utf-8") as f:
        products: list[dict] = json.load(f)

    updated: list[dict] = []

    for i, product in enumerate(products, 1):
        code = product.get("product_code", "")
        folder_path = os.path.join(CRAWL_DIR, code)

        print(f"[{i:3d}/{len(products)}] {code}", end=" ")

        if not os.path.isdir(folder_path):
            print("→ 폴더 없음, 건너뜀")
            updated.append({k: v for k, v in product.items() if k not in REMOVE_FIELDS})
            continue

        rename_map = rename_images_in_folder(folder_path)

        product_count = sum(1 for v in rename_map.values() if v.startswith("product_"))
        detail_count = sum(1 for v in rename_map.values() if v.startswith("detail_"))
        print(f"→ 상품 이미지 {product_count}개 / 상세 이미지 {detail_count}개")

        new_images = [
            build_new_image_path(img, rename_map)
            for img in product.get("images", [])
            if os.path.basename(img) in rename_map
        ]

        entry = {k: v for k, v in product.items() if k not in REMOVE_FIELDS}
        entry["images"] = new_images
        updated.append(entry)

    with open(MANIFEST_OUT, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
    print(f"\nmanifest 저장 완료: {MANIFEST_OUT}")

    csv_fields = ["product_code", "name", "price", "volume", "product_image_count", "detail_image_count"]
    with open(CSV_OUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(csv_fields)
        for entry in updated:
            images = entry.get("images", [])
            p_cnt = sum(1 for img in images if os.path.basename(img).startswith("product_"))
            d_cnt = sum(1 for img in images if os.path.basename(img).startswith("detail_"))
            writer.writerow([
                entry.get("product_code"),
                entry.get("name"),
                entry.get("price"),
                entry.get("volume"),
                p_cnt,
                d_cnt,
            ])
    print(f"CSV 저장 완료: {CSV_OUT}")


if __name__ == "__main__":
    main()
